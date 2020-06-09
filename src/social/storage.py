def write_file(f,path):
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def rename_file(path,):
    #TODO continue rename file
    pass