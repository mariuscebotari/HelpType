from django import forms
from django.utils.safestring import mark_safe

class CodeMirrorWidget(forms.Textarea):
    class Media:
        css = {
            'all': [
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/theme/material.min.css',
            ]
        }
        js = [
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/xml/xml.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/javascript/javascript.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/css/css.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/htmlmixed/htmlmixed.min.js',
        ]

    def __init__(self, attrs=None):
        default = {'class': 'codemirror-html', 'style': 'height:400px;'}
        if attrs:
            default.update(attrs)
        super().__init__(attrs=default)

    def render(self, name, value, attrs=None, renderer=None):
        textarea = super().render(name, value, attrs, renderer)
        js = """
        <script>
        (function(){
          function init() {
            var textareas = document.querySelectorAll('textarea.codemirror-html');
            textareas.forEach(function(ta){
              if (ta.classList.contains('cm-initialized')) return;
              var editor = CodeMirror.fromTextArea(ta, {
                mode: 'htmlmixed',
                lineNumbers: true,
                theme: 'material',
                matchBrackets: true,
                autoCloseTags: true,
                lineWrapping: true
              });
              ta.classList.add('cm-initialized');
              editor.on('change', function(){ editor.save(); });
            });
          }
          if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
          } else { init(); }
        })();
        </script>
        """
        return mark_safe(textarea + js)