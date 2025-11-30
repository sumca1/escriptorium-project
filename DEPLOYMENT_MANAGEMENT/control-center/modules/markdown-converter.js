// ========================================
// ממיר Markdown ל-HTML מעוצב (MD → HTML Converter)
// ========================================

class MarkdownToHTMLConverter {
    constructor() {
        this.rtlPattern = /[\u0590-\u05FF\u0600-\u06FF]/; // עברית וערבית
    }

    // ========================================
    // המרת Markdown ל-HTML
    // ========================================
    convert(markdown) {
        let html = markdown;

        // כותרות (Headers)
        html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');

        // Bold (מודגש)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

        // Italic (נטוי)
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        html = html.replace(/_(.*?)_/g, '<em>$1</em>');

        // Code inline (קוד בשורה)
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Code blocks (בלוקי קוד)
        html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            const language = lang || 'text';
            return `<pre><code class="language-${language}">${this.escapeHtml(code.trim())}</code></pre>`;
        });

        // Links (קישורים)
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

        // רשימות לא ממוספרות (Unordered Lists)
        html = html.replace(/^\- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // רשימות ממוספרות (Ordered Lists)
        html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

        // טבלאות (Tables)
        html = this.convertTables(html);

        // פסקאות (Paragraphs)
        html = html.split('\n\n').map(para => {
            if (para.trim() && !para.startsWith('<')) {
                return `<p>${para.trim()}</p>`;
            }
            return para;
        }).join('\n');

        // הוספת dir="rtl" לאלמנטים עם עברית
        html = this.addRTLSupport(html);

        return html;
    }

    // ========================================
    // המרת טבלאות
    // ========================================
    convertTables(markdown) {
        const tableRegex = /(\|.+\|\n)+/g;
        return markdown.replace(tableRegex, (match) => {
            const rows = match.trim().split('\n');
            if (rows.length < 2) return match;

            let html = '<table class="markdown-table">\n';
            
            // Header
            const headerCells = rows[0].split('|').filter(c => c.trim());
            html += '<thead><tr>\n';
            headerCells.forEach(cell => {
                html += `<th>${cell.trim()}</th>\n`;
            });
            html += '</tr></thead>\n';

            // Body (דלג על שורת ההפרדה)
            html += '<tbody>\n';
            for (let i = 2; i < rows.length; i++) {
                const cells = rows[i].split('|').filter(c => c.trim());
                html += '<tr>\n';
                cells.forEach(cell => {
                    html += `<td>${cell.trim()}</td>\n`;
                });
                html += '</tr>\n';
            }
            html += '</tbody>\n</table>\n';

            return html;
        });
    }

    // ========================================
    // הוספת תמיכה RTL
    // ========================================
    addRTLSupport(html) {
        // זיהוי עברית בכותרות
        html = html.replace(/<(h[1-6])>([^<]+)<\/\1>/g, (match, tag, content) => {
            if (this.rtlPattern.test(content)) {
                return `<${tag} dir="rtl">${content}</${tag}>`;
            }
            return match;
        });

        // זיהוי עברית בפסקאות
        html = html.replace(/<p>([^<]+)<\/p>/g, (match, content) => {
            if (this.rtlPattern.test(content)) {
                return `<p dir="rtl">${content}</p>`;
            }
            return match;
        });

        // זיהוי עברית בתאי טבלה
        html = html.replace(/<(td|th)>([^<]+)<\/\1>/g, (match, tag, content) => {
            if (this.rtlPattern.test(content)) {
                return `<${tag} dir="rtl">${content}</${tag}>`;
            }
            return match;
        });

        return html;
    }

    // ========================================
    // Escape HTML
    // ========================================
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // ========================================
    // יצירת HTML מלא עם CSS
    // ========================================
    createFullHTML(title, markdownContent) {
        const bodyHTML = this.convert(markdownContent);
        
        return `<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <style>
        /* ========================================
           עיצוב כללי (General Styling)
           ======================================== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
            color: #0f172a;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            min-height: 100vh;
        }

        /* ========================================
           מיכל תוכן (Content Container)
           ======================================== */
        .content {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        /* ========================================
           כותרות (Headers)
           ======================================== */
        h1 {
            color: #1e3a8a;
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid #3b82f6;
        }

        h2 {
            color: #1e40af;
            font-size: 2rem;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            padding-right: 1rem;
            border-right: 4px solid #60a5fa;
        }

        h3 {
            color: #1e40af;
            font-size: 1.5rem;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
        }

        /* ========================================
           פסקאות (Paragraphs)
           ======================================== */
        p {
            margin-bottom: 1.25rem;
            text-align: justify;
        }

        /* ========================================
           קוד (Code)
           ======================================== */
        code {
            background: #f1f5f9;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9rem;
            color: #dc2626;
            direction: ltr;
            display: inline-block;
        }

        pre {
            background: #1e293b;
            color: #e2e8f0;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
            direction: ltr;
            text-align: left;
        }

        pre code {
            background: none;
            color: inherit;
            padding: 0;
        }

        /* ========================================
           רשימות (Lists)
           ======================================== */
        ul, ol {
            margin: 1rem 0 1rem 2rem;
        }

        li {
            margin-bottom: 0.5rem;
            line-height: 1.6;
        }

        /* ========================================
           טבלאות (Tables)
           ======================================== */
        .markdown-table {
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .markdown-table thead {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
        }

        .markdown-table th {
            padding: 1rem;
            text-align: right;
            font-weight: 600;
            border-bottom: 2px solid #1e40af;
        }

        .markdown-table td {
            padding: 0.875rem 1rem;
            border-bottom: 1px solid #e2e8f0;
        }

        .markdown-table tbody tr:nth-child(even) {
            background: #f8fafc;
        }

        .markdown-table tbody tr:hover {
            background: #e0f2fe;
            transition: background 0.2s;
        }

        /* ========================================
           קישורים (Links)
           ======================================== */
        a {
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.2s;
        }

        a:hover {
            color: #1e40af;
            border-bottom-color: #1e40af;
        }

        /* ========================================
           הדגשות (Emphasis)
           ======================================== */
        strong {
            color: #1e40af;
            font-weight: 600;
        }

        em {
            color: #475569;
            font-style: italic;
        }

        /* ========================================
           אמוג'י וסמלים (Emojis & Icons)
           ======================================== */
        .content h1::before,
        .content h2::before {
            margin-left: 0.5rem;
        }

        /* ========================================
         תמיכה במסכים קטנים (Responsive)
           ======================================== */
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }

            .content {
                padding: 1.5rem;
            }

            h1 {
                font-size: 1.875rem;
            }

            h2 {
                font-size: 1.5rem;
            }

            .markdown-table {
                font-size: 0.875rem;
            }
        }

        /* ========================================
           כפתור חזרה (Back Button)
           ======================================== */
        .back-btn {
            position: fixed;
            top: 2rem;
            left: 2rem;
            background: white;
            color: #1e40af;
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            z-index: 1000;
        }

        .back-btn:hover {
            background: #1e40af;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        }
    </style>
</head>
<body>
    <a href="/dashboard.html" class="back-btn">🏠 חזרה לדשבורד</a>
    <div class="content">
        ${bodyHTML}
    </div>
</body>
</html>`;
    }
}

// ייצוא
const converter = new MarkdownToHTMLConverter();
export default converter;
