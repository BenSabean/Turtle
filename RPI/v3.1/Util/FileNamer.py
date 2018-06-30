import os.path

def FileNamer(file, ext):
  __tmp = """{path}.{extension}""".format(path=file, extension=ext)
  if not os.path.isfile(__tmp):
    return __tmp

  for i in range(1,100): 
    __tmp = """{path}_{num}.{extension}""".format(path=file, num=i, extension=ext)
    if not os.path.isfile(__tmp):
        return __tmp

  return None


if __name__ == "__main__":
  print(FileNamer("test","csv"))

