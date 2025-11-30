"""
TABA Pipeline Executor
Handles execution of external TABA pipeline for alignment jobs
"""
import os
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


class TABAPipelineExecutor:
    """
    Executor for TABA Pipeline - runs external alignment process
    """
    
    def __init__(self, job):
        """
        Initialize executor with alignment job
        
        Args:
            job: AlignmentJob instance
        """
        import tempfile
        from pathlib import Path
        
        self.job = job
        self.taba_path = getattr(settings, 'TABA_PIPELINE_PATH', None)
        # Security: Use settings value if provided, otherwise use secure temp dir
        # nosec B108: Using tempfile.gettempdir() for cross-platform secure temp
        self.work_dir = getattr(settings, 'TABA_WORK_DIR', 
                                str(Path(tempfile.gettempdir()) / 'taba_work'))  # nosec B108
        self.output_dir = getattr(settings, 'TABA_OUTPUT_DIR', 
                                  str(Path(tempfile.gettempdir()) / 'taba_output'))  # nosec B108
        self.conda_env = getattr(settings, 'TABA_CONDA_ENV', 'taba_alignment')
        
    def validate_setup(self):
        """
        Validate that TABA pipeline is properly installed
        
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        if not self.taba_path:
            return False, "TABA_PIPELINE_PATH not configured in settings"
        
        if not os.path.exists(self.taba_path):
            return False, f"TABA pipeline not found at: {self.taba_path}"
        
        main_script = os.path.join(self.taba_path, 'main.py')
        if not os.path.exists(main_script):
            return False, f"main.py not found in TABA pipeline: {main_script}"
        
        return True, None
    
    def prepare_workspace(self):
        """
        Prepare working directories for TABA execution
        
        Returns:
            dict: Paths to work directories
        """
        job_id = self.job.pk
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create job-specific directories
        job_work_dir = os.path.join(self.work_dir, f'job_{job_id}_{timestamp}')
        job_output_dir = os.path.join(self.output_dir, f'job_{job_id}_{timestamp}')
        
        os.makedirs(job_work_dir, exist_ok=True)
        os.makedirs(job_output_dir, exist_ok=True)
        
        # Create subdirectories
        paths = {
            'work': job_work_dir,
            'output': job_output_dir,
            'ocr': os.path.join(job_work_dir, 'ocr'),
            'gt': os.path.join(job_work_dir, 'ground_truth'),
            'results': os.path.join(job_output_dir, 'results'),
        }
        
        for path in paths.values():
            os.makedirs(path, exist_ok=True)
        
        return paths
    
    def export_ocr_to_xml(self, paths):
        """
        Export OCR transcription to XML format for TABA
        
        Args:
            paths: Dictionary of workspace paths
            
        Returns:
            str: Path to exported XML file
        """
        from core.models import DocumentPart
        
        document = self.job.document
        transcription = self.job.ocr_transcription
        
        logger.info(f"Exporting OCR from document {document.pk}, transcription {transcription.pk}")
        
        # Get all parts of the document
        parts = DocumentPart.objects.filter(document=document).order_by('order')
        
        xml_path = os.path.join(paths['ocr'], f'document_{document.pk}.xml')
        
        # Export to PAGE XML format (eScriptorium standard)
        # TODO: Implement actual XML export using eScriptorium's export functionality
        # For now, create a placeholder
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">\n')
            
            for part in parts:
                # Get transcription content for this part
                # lines = transcription.get_lines_for_part(part)  # TODO: Implement
                f.write(f'  <!-- Part {part.pk}: {part.name} -->\n')
            
            f.write('</PcGts>\n')
        
        logger.info(f"OCR exported to: {xml_path}")
        return xml_path
    
    def export_ground_truth(self, paths):
        """
        Export Ground Truth corpus to text files for TABA
        
        Args:
            paths: Dictionary of workspace paths
            
        Returns:
            list: Paths to exported GT files
        """
        corpus = self.job.gt_corpus
        gt_texts = corpus.texts.all()
        
        logger.info(f"Exporting {gt_texts.count()} GT texts from corpus {corpus.name}")
        
        gt_files = []
        for text in gt_texts:
            filename = text.filename or f"{text.pk}_{text.title}.txt"
            file_path = os.path.join(paths['gt'], filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text.content)
            
            gt_files.append(file_path)
            logger.debug(f"Exported GT: {filename} ({text.character_count} chars)")
        
        logger.info(f"Exported {len(gt_files)} GT files to: {paths['gt']}")
        return gt_files
    
    def build_taba_command(self, paths, ocr_xml, gt_files):
        """
        Build TABA pipeline command with parameters
        
        Args:
            paths: Dictionary of workspace paths
            ocr_xml: Path to OCR XML file
            gt_files: List of GT file paths
            
        Returns:
            list: Command array for subprocess
        """
        # TABA main.py command structure
        cmd = [
            'conda', 'run', '-n', self.conda_env,
            'python', os.path.join(self.taba_path, 'main.py'),
            '--ocr', ocr_xml,
            '--gt-dir', paths['gt'],
            '--output', paths['results'],
            '--n', str(self.job.passim_n),
            '--cores', str(self.job.passim_cores),
            '--memory', f"{self.job.passim_memory}g",
            '--driver-memory', f"{self.job.passim_driver_memory}g",
            '--threshold', str(self.job.levenshtein_threshold),
        ]
        
        return cmd
    
    def run_pipeline(self, cmd):
        """
        Execute TABA pipeline command
        
        Args:
            cmd: Command array
            
        Returns:
            tuple: (bool, str) - (success, output/error)
        """
        logger.info(f"Running TABA pipeline: {' '.join(cmd)}")
        
        try:
            # Run TABA pipeline
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output (for progress tracking)
            stdout_lines = []
            stderr_lines = []
            
            for line in process.stdout:
                stdout_lines.append(line)
                logger.info(f"TABA: {line.strip()}")
                
                # Update job progress based on output
                if 'Progress:' in line:
                    try:
                        progress = int(line.split('Progress:')[1].split('%')[0].strip())
                        self.job.progress = progress
                        self.job.save(update_fields=['progress'])
                    except (ValueError, IndexError):
                        pass
            
            for line in process.stderr:
                stderr_lines.append(line)
                logger.warning(f"TABA stderr: {line.strip()}")
            
            # Wait for completion
            return_code = process.wait()
            
            if return_code == 0:
                logger.info("TABA pipeline completed successfully")
                return True, '\n'.join(stdout_lines)
            else:
                error_msg = '\n'.join(stderr_lines) or "Unknown error"
                logger.error(f"TABA pipeline failed with code {return_code}: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.exception(f"Error running TABA pipeline: {e}")
            return False, str(e)
    
    def import_results(self, paths):
        """
        Import TABA alignment results back to eScriptorium
        
        Args:
            paths: Dictionary of workspace paths
            
        Returns:
            tuple: (bool, int) - (success, num_aligned_lines)
        """
        from .models import AlignmentResult
        from core.models import DocumentPart
        
        results_dir = paths['results']
        
        # Look for result JSON files
        result_files = list(Path(results_dir).glob('*.json'))
        
        logger.info(f"Found {len(result_files)} result files in {results_dir}")
        
        total_lines = 0
        aligned_texts = set()
        
        for result_file in result_files:
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                
                # Parse result data
                part_pk = result_data.get('part_pk')
                part_title = result_data.get('part_title', f'Part {part_pk}')
                gt_text_pk = result_data.get('gt_text_pk')
                aligned_lines = result_data.get('aligned_lines', [])
                clusters = result_data.get('clusters', [])
                avg_levenshtein = result_data.get('avg_levenshtein', 0.0)
                
                # Create AlignmentResult record
                if gt_text_pk:
                    from .models import GroundTruthText
                    gt_text = GroundTruthText.objects.get(pk=gt_text_pk)
                    
                    result = AlignmentResult.objects.create(
                        job=self.job,
                        part_pk=part_pk,
                        part_title=part_title,
                        gt_text=gt_text,
                        total_aligned_lines=len(aligned_lines),
                        aligned_clusters=clusters,
                        max_cluster_size=max(clusters) if clusters else 0,
                        average_levenshtein_ratio=avg_levenshtein,
                    )
                    
                    total_lines += len(aligned_lines)
                    aligned_texts.add(gt_text.title)
                    
                    logger.info(f"Imported result for part {part_pk}: {len(aligned_lines)} lines")
                
            except Exception as e:
                logger.error(f"Error importing result from {result_file}: {e}")
                continue
        
        # Update job statistics
        self.job.total_aligned_lines = total_lines
        self.job.aligned_gt_texts = list(aligned_texts)
        self.job.results_path = str(results_dir)
        self.job.save()
        
        logger.info(f"Import completed: {total_lines} total lines from {len(aligned_texts)} GT texts")
        
        return True, total_lines
    
    def execute(self):
        """
        Main execution method - runs the complete TABA pipeline
        
        Returns:
            tuple: (bool, str) - (success, message)
        """
        # Update job status
        self.job.status = 'preparing'
        self.job.progress = 0
        self.job.started_at = datetime.now()
        self.job.save()
        
        try:
            # 1. Validate setup
            valid, error = self.validate_setup()
            if not valid:
                raise Exception(f"TABA setup validation failed: {error}")
            
            logger.info(f"Starting TABA pipeline for job {self.job.pk}: {self.job.name}")
            
            # 2. Prepare workspace
            self.job.progress = 5
            self.job.save(update_fields=['progress'])
            paths = self.prepare_workspace()
            logger.info(f"Workspace prepared: {paths['work']}")
            
            # 3. Export OCR
            self.job.status = 'preparing'
            self.job.progress = 10
            self.job.save()
            ocr_xml = self.export_ocr_to_xml(paths)
            
            # 4. Export Ground Truth
            self.job.progress = 20
            self.job.save(update_fields=['progress'])
            gt_files = self.export_ground_truth(paths)
            
            # 5. Build TABA command
            self.job.progress = 25
            self.job.save(update_fields=['progress'])
            cmd = self.build_taba_command(paths, ocr_xml, gt_files)
            
            # 6. Run TABA pipeline
            self.job.status = 'running_passim'
            self.job.progress = 30
            self.job.save()
            
            success, output = self.run_pipeline(cmd)
            
            if not success:
                raise Exception(f"TABA pipeline execution failed: {output}")
            
            # 7. Import results
            self.job.status = 'importing'
            self.job.progress = 90
            self.job.save()
            
            success, num_lines = self.import_results(paths)
            
            if not success:
                raise Exception("Failed to import TABA results")
            
            # 8. Complete
            self.job.status = 'completed'
            self.job.progress = 100
            self.job.completed_at = datetime.now()
            self.job.save()
            
            message = f"TABA pipeline completed successfully: {num_lines} lines aligned"
            logger.info(message)
            
            return True, message
            
        except Exception as e:
            # Handle failure
            error_msg = str(e)
            logger.exception(f"TABA pipeline failed: {error_msg}")
            
            self.job.status = 'failed'
            self.job.error_message = error_msg
            self.job.completed_at = datetime.now()
            self.job.save()
            
            return False, error_msg
