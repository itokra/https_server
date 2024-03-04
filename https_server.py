#!/usr/bin/env python3

import os
import ssl
import http.server as hs

class options:
    keySSL_CRT_Filename : str = "sslcert.crt"
    keySSL_KEY_Filename : str = "sslcert.key"
    keyMoviesFolder : str = './Movies/'

    colorBlue = '\033[94m'
    colorGreen = '\033[92m'
    colorGray = '\033[90m'
    colorReset = '\033[0m'

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def run_server(server_class=hs.HTTPServer, handler_class=hs.SimpleHTTPRequestHandler):
    print('Starting server …', end='')

    server_address = ('', 443)
    httpd = server_class(server_address, handler_class)

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(options.keySSL_CRT_Filename, options.keySSL_KEY_Filename)

    httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

    print(f'\rServer is working')
    httpd.serve_forever()

def check_and_prepare_certificates(passes_count=False):
    if os.path.exists(options.keySSL_CRT_Filename) == True and os.path.exists(options.keySSL_KEY_Filename) == True:
        print(f'\rCertificates are OK        ')
        return

    print('Generating certificates …', end='    ')

    try:
        os.remove(options.keySSL_CRT_Filename)
        os.remove(options.keySSL_KEY_Filename)
    except:
        pass

    if passes_count == False:
        os.system(f'openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out ./{options.keySSL_CRT_Filename} -keyout ./{options.keySSL_KEY_Filename} -verbose -subj "/C=UA/ST=Luhansk/L=Kadiivka/O=A26/OU=org/CN=A26.com" 2>/dev/null')
    check_and_prepare_certificates(True)

def prepare_movies_list():
    result = ''

    print('Generating files list …', end='')

    for filename in os.listdir(options.keyMoviesFolder):
        if filename.startswith('.') == False:
            movie_path = options.keyMoviesFolder + filename
            st = os.stat(movie_path)
            if os.path.isfile(movie_path) == True:
                file_stats = os.stat(movie_path)
                file_size = sizeof_fmt(file_stats.st_size)

                href_link = f'<a class="button" href="{movie_path}">{filename} ({file_size})</a>\n'
                result = result + href_link

    with open('./index.template', 'r') as fr:
        template = fr.read().replace('####', result)
        fr.close()
    
        with open('./index.html', 'w') as fw:
            fw.write(template)
            fw.close()

    print(f'\rFiles list is OK       ')

if __name__ == '__main__':
    os.chdir(os.getcwd())

    check_and_prepare_certificates()
    prepare_movies_list()

    run_server()
