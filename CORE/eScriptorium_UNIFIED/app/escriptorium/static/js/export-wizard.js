/**
 * export-wizard.js
 * Handles PDF/DOCX export wizard form behavior and routing
 * Part of BiblIA Dataset enhancements
 */

(function() {
    'use strict';
    
    /**
     * Initialize export wizard behavior
     */
    function initExportWizard() {
        const fileFormatSelect = $('#id_file_format');
        const exportForm = $('#process-part-form-export');
        
        if (!fileFormatSelect.length || !exportForm.length) {
            return; // Not on export wizard page
        }
        
        // Add PDF and DOCX options to file_format dropdown if not exists
        if (fileFormatSelect.find('option[value="pdf"]').length === 0) {
            fileFormatSelect.append('<option value="pdf">PDF</option>');
        }
        if (fileFormatSelect.find('option[value="docx"]').length === 0) {
            fileFormatSelect.append('<option value="docx">DOCX</option>');
        }
        
        // Show/hide PDF/DOCX specific options based on format
        function updateExportOptions() {
            const format = fileFormatSelect.val();
            const pdfDocxOptions = $('#pdf-docx-options');
            const pdfLayoutGroup = $('#pdf-layout-group');
            const docxImagesGroup = $('#docx-images-group');
            const docxParagraphGroup = $('#docx-paragraph-group');
            
            if (format === 'pdf' || format === 'docx') {
                pdfDocxOptions.show();
                
                // Show/hide format-specific options
                if (format === 'pdf') {
                    pdfLayoutGroup.show();
                    docxImagesGroup.hide();
                    docxParagraphGroup.hide();
                } else if (format === 'docx') {
                    pdfLayoutGroup.hide();
                    docxImagesGroup.show();
                    docxParagraphGroup.show();
                }
            } else {
                pdfDocxOptions.hide();
            }
        }
        
        // Override form submission for PDF/DOCX
        exportForm.on('submit', function(e) {
            const format = fileFormatSelect.val();
            const documentPk = exportForm.data('document-pk');
            
            if (format === 'pdf' || format === 'docx') {
                e.preventDefault(); // Prevent default submission
                
                // Build export URL
                const exportUrl = format === 'pdf' 
                    ? `/document/${documentPk}/export/pdf/`
                    : `/document/${documentPk}/export/docx/`;
                
                // Get form data
                const formData = new FormData();
                
                // Add transcription
                const transcriptionId = $('#id_transcription').val();
                if (transcriptionId) {
                    formData.append('transcription_id', transcriptionId);
                }
                
                // Add common options
                formData.append('include_metadata', $('#include_metadata').is(':checked') ? 'true' : 'false');
                formData.append('font_size', $('#font_size').val() || '12');
                formData.append('line_spacing', $('#line_spacing').val() || '1.5');
                
                // Add format-specific options
                if (format === 'pdf') {
                    formData.append('layout', $('#pdf_layout').val() || 'text_only');
                } else if (format === 'docx') {
                    formData.append('include_images', $('#include_images_docx').is(':checked') ? 'true' : 'false');
                    formData.append('paragraph_per_line', $('#paragraph_per_line').is(':checked') ? 'true' : 'false');
                }
                
                // Get CSRF token
                const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
                
                // Submit export request
                $.ajax({
                    url: exportUrl,
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    xhrFields: {
                        responseType: 'blob' // Important for file download
                    },
                    success: function(data, status, xhr) {
                        // Get filename from Content-Disposition header
                        const disposition = xhr.getResponseHeader('Content-Disposition');
                        let filename = `export.${format}`;
                        if (disposition) {
                            const filenameMatch = disposition.match(/filename="(.+)"/);
                            if (filenameMatch) {
                                filename = filenameMatch[1];
                            }
                        }
                        
                        // Create download link
                        const blob = new Blob([data], { 
                            type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        });
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                        
                        // Close modal
                        $('#process-modal-export').modal('hide');
                        
                        // Show success message
                        if (typeof alertify !== 'undefined') {
                            alertify.success(`${format.toUpperCase()} exported successfully!`);
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Export failed:', error);
                        
                        // Try to read error message from response
                        let errorMsg = 'Export failed. Please try again.';
                        if (xhr.responseJSON && xhr.responseJSON.error) {
                            errorMsg = xhr.responseJSON.error;
                        }
                        
                        // Show error message
                        if (typeof alertify !== 'undefined') {
                            alertify.error(errorMsg);
                        } else {
                            alert(errorMsg);
                        }
                    }
                });
                
                return false;
            }
            
            // Let default form submission happen for other formats
            return true;
        });
        
        // Bind change event
        fileFormatSelect.on('change', updateExportOptions);
        
        // Store document PK in form data attribute
        const documentPk = window.location.pathname.match(/document\/(\d+)/);
        if (documentPk) {
            exportForm.attr('data-document-pk', documentPk[1]);
        }
        
        // Initial call
        updateExportOptions();
    }
    
    // Initialize when DOM is ready
    $(document).ready(function() {
        initExportWizard();
        
        // Re-initialize when modal is shown (in case of dynamic content)
        $('#process-modal-export').on('shown.bs.modal', function() {
            initExportWizard();
        });
    });
    
})();
