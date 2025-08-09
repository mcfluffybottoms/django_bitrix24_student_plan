import os
from tempfile import NamedTemporaryFile
from wsgiref.util import FileWrapper

from django.http import HttpResponse, Http404
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

import settings
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from task5.models.contact_loader import load_data, get_data
from task5.models.forms import UploadFileForm, ExportFileForm, get_format_from_form


@main_auth(on_cookies=True)
def start_task5(request):
    but = request.bitrix_user_token
    context = {
        "message": ""
    }
    if request.method == "POST":
        if 'import' in request.POST:
            import_form = UploadFileForm(request.POST)
            export_form = ExportFileForm()
            if import_form.is_valid():
                loaded_file = request.FILES.get('file')
                if not loaded_file:
                    message = "Файл не был загружен."
                    context['message'] = message
                else:
                    fs = FileSystemStorage()
                    filename = fs.save(loaded_file.name, loaded_file)
                    uploaded_file_path = fs.path(filename)
                    load_result = load_data(but, uploaded_file_path)
                    if load_result.get('done'):
                        context['message'] = "Файл был удачно загружен и обработан!"
                    else:
                        context['message'] = load_result.get('error')
                    fs.delete(filename)
        elif 'export' in request.POST:
            import_form = UploadFileForm()
            export_form = ExportFileForm(request.POST)
            if export_form.is_valid():
                file_format = get_format_from_form(export_form)
                with NamedTemporaryFile(suffix=f'.{file_format}', delete=False) as result_file:
                    export_result = get_data(but, file_format, result_file)
                    if not export_result.get('done'):
                        context['message'] = export_result.get('error', 'Произошла ошибка при экспорте.')
                        return render(request, 'task5.html', context)
                with open(result_file.name, 'rb') as f:
                    wrapper = FileWrapper(f)
                    response = HttpResponse(wrapper, content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="export.{file_format}"'
                    return response
                response = HttpResponse(wrapper, content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="export{file_format}"'
                return response

    else:
        import_form = UploadFileForm()
        export_form = ExportFileForm()
    context['import_form'] = import_form
    context['export_form'] = export_form
    return render(request, 'task5.html', context)