/**
 * SegmOnto Compliance Checker for eScriptorium
 * Adapted from HTR-United browser extension
 * https://github.com/HTR-United/browser-extension-segmonto
 */

export class SegmontoChecker {
    constructor() {
        // SegmOnto valid zone types
        this.validZones = /^(CustomZone|DamageZone|GraphicZone|DigitizationArtefactZone|DropCapitalZone|MainZone|MarginTextZone|MusicZone|NumberingZone|QuireMarksZone|RunningTitleZone|SealZone|StampZone|TableZone|TitlePageZone)(\:.*)?(#.*)?$/;
        
        // SegmOnto valid line types
        this.validLines = /^(CustomLine|DefaultLine|DropCapitalLine|HeadingLine|InterlinearLine|MusicLine)(\:.*)?(#.*)?$/;
    }

    /**
     * Check if a typology is valid for the given type
     * @param {string} typology - The typology string to check
     * @param {string} type - Either 'zone' or 'line'
     * @returns {boolean}
     */
    checkValidity(typology, type) {
        if (typology === undefined || typology === null) {
            return false;
        }
        
        if (type === 'line' && this.validLines.test(typology)) {
            return true;
        } else if (type === 'zone' && this.validZones.test(typology)) {
            return true;
        }
        
        return false;
    }

    /**
     * Check regions (zones) compliance
     * @param {Array} regions - Array of region objects from store
     * @param {Object} regionTypes - Dictionary of region type IDs to names
     * @returns {Object} Results with valid count and errors
     */
    checkRegions(regions, regionTypes) {
        const errors = [];
        let validCount = 0;

        regions.forEach(region => {
            if (!region.typology) {
                errors.push({
                    id: region.pk || region.id,
                    type: 'region',
                    error: 'No typology assigned',
                    severity: 'warning'
                });
            } else {
                const typologyName = regionTypes[region.typology];
                if (!this.checkValidity(typologyName, 'zone')) {
                    errors.push({
                        id: region.pk || region.id,
                        type: 'region',
                        typology: typologyName,
                        error: `Invalid SegmOnto zone type: "${typologyName}"`,
                        severity: 'error'
                    });
                } else {
                    validCount++;
                }
            }
        });

        return {
            total: regions.length,
            valid: validCount,
            invalid: regions.length - validCount,
            errors: errors,
            percentage: regions.length > 0 ? (validCount / regions.length * 100).toFixed(2) : 100
        };
    }

    /**
     * Check lines compliance
     * @param {Array} lines - Array of line objects from store
     * @param {Object} lineTypes - Dictionary of line type IDs to names
     * @returns {Object} Results with valid count and errors
     */
    checkLines(lines, lineTypes) {
        const errors = [];
        let validCount = 0;

        lines.forEach(line => {
            let lineErrors = 0;

            // Check typology
            if (!line.typology) {
                errors.push({
                    id: line.pk || line.id,
                    order: line.order,
                    type: 'line',
                    error: 'No typology assigned',
                    severity: 'warning'
                });
                lineErrors++;
            } else {
                const typologyName = lineTypes[line.typology];
                if (!this.checkValidity(typologyName, 'line')) {
                    errors.push({
                        id: line.pk || line.id,
                        order: line.order,
                        type: 'line',
                        typology: typologyName,
                        error: `Invalid SegmOnto line type: "${typologyName}"`,
                        severity: 'error'
                    });
                    lineErrors++;
                }
            }

            // Check if line belongs to a region
            if (!line.region) {
                errors.push({
                    id: line.pk || line.id,
                    order: line.order,
                    type: 'line',
                    error: 'Line does not belong to any region',
                    severity: 'warning'
                });
                lineErrors++;
            }

            if (lineErrors === 0) {
                validCount++;
            }
        });

        return {
            total: lines.length,
            valid: validCount,
            invalid: lines.length - validCount,
            errors: errors,
            percentage: lines.length > 0 ? (validCount / lines.length * 100).toFixed(2) : 100
        };
    }

    /**
     * Get severity badge class
     * @param {number} percentage - Percentage of valid items
     * @returns {string} Bootstrap badge class
     */
    getSeverityClass(percentage) {
        if (percentage === 100) return 'success';
        if (percentage >= 50) return 'warning';
        return 'danger';
    }

    /**
     * Format results for display
     * @param {Object} regionResults - Results from checkRegions
     * @param {Object} lineResults - Results from checkLines
     * @returns {Object} Formatted results
     */
    formatResults(regionResults, lineResults) {
        return {
            regions: {
                ...regionResults,
                badgeClass: this.getSeverityClass(parseFloat(regionResults.percentage))
            },
            lines: {
                ...lineResults,
                badgeClass: this.getSeverityClass(parseFloat(lineResults.percentage))
            },
            overall: {
                totalValid: regionResults.valid + lineResults.valid,
                totalInvalid: regionResults.invalid + lineResults.invalid,
                totalItems: regionResults.total + lineResults.total,
                percentage: ((regionResults.valid + lineResults.valid) / 
                           (regionResults.total + lineResults.total) * 100).toFixed(2)
            }
        };
    }

    /**
     * Main check function - analyzes current document state
     * @param {Object} store - Vuex store instance
     * @returns {Object} Complete check results
     */
    checkDocument(store) {
        const state = store.state;
        
        // Get current document data
        const regions = state.document?.regions || [];
        const lines = state.lines?.all || [];
        
        // Get typology dictionaries
        const regionTypes = {};
        const lineTypes = {};
        
        // Build type dictionaries from document metadata
        if (state.document?.valid_block_types) {
            state.document.valid_block_types.forEach(type => {
                regionTypes[type.pk || type.id] = type.name;
            });
        }
        
        if (state.document?.valid_line_types) {
            state.document.valid_line_types.forEach(type => {
                lineTypes[type.pk || type.id] = type.name;
            });
        }

        // Run checks
        const regionResults = this.checkRegions(regions, regionTypes);
        const lineResults = this.checkLines(lines, lineTypes);

        // Format and return
        return this.formatResults(regionResults, lineResults);
    }

    /**
     * Generate HTML report
     * @param {Object} results - Results from checkDocument
     * @returns {string} HTML string
     */
    generateHTMLReport(results) {
        const { regions, lines, overall } = results;
        
        let html = `
            <div class="segmonto-report">
                <h4>SegmOnto Compliance Report</h4>
                
                <div class="alert alert-${overall.percentage === '100.00' ? 'success' : 'warning'}">
                    <strong>Overall:</strong> ${overall.totalValid}/${overall.totalItems} items valid (${overall.percentage}%)
                </div>
                
                <div class="region-results">
                    <h5>Regions <span class="badge bg-${regions.badgeClass}">${regions.valid}/${regions.total}</span></h5>
                    ${this._generateErrorList(regions.errors, 'region')}
                </div>
                
                <div class="line-results">
                    <h5>Lines <span class="badge bg-${lines.badgeClass}">${lines.valid}/${lines.total}</span></h5>
                    ${this._generateErrorList(lines.errors, 'line')}
                </div>
            </div>
        `;
        
        return html;
    }

    /**
     * Generate error list HTML
     * @private
     */
    _generateErrorList(errors, type) {
        if (errors.length === 0) {
            return '<p class="text-success">✓ All items are valid!</p>';
        }
        
        let html = '<ul class="segmonto-errors">';
        errors.forEach(error => {
            const icon = error.severity === 'error' ? '❌' : '⚠️';
            html += `<li class="text-${error.severity === 'error' ? 'danger' : 'warning'}">
                ${icon} ${type.charAt(0).toUpperCase() + type.slice(1)} ${error.id}${error.order !== undefined ? ` (Order ${error.order + 1})` : ''}: 
                ${error.error}${error.typology ? ` - "${error.typology}"` : ''}
            </li>`;
        });
        html += '</ul>';
        
        return html;
    }
}

// Export singleton instance
export const segmontoChecker = new SegmontoChecker();
