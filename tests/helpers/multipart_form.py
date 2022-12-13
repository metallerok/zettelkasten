import io


def create_multipart(data, field_name: str, filename: str, content_type: str = None):
    boundary = '----WebKitFormBoundary' + "D5X9HfRGQXhTZn2y"

    buff = io.BytesIO()
    buff.write(b'--')
    buff.write(boundary.encode())
    buff.write(b'\r\n')
    buff.write(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode())
    buff.write(b'\r\n')
    buff.write(('Content-Type: %s' % content_type).encode())
    buff.write(b'\r\n')
    buff.write(b'\r\n')
    buff.write(data)
    buff.write(b'\r\n')
    buff.write(boundary.encode())
    buff.write(b'--\r\n')

    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}', 'Content-Length': str(buff.tell())}

    return buff.getvalue(), headers
