# pip install -r requirements.txt
# Author:Bauyrzhan.Dyussekeyev
'''
Данный скрипт был разработан в результате анализа файлов со следующими хэшами:

4FB03873B77F522FB75B6F6088F8CF8FD88CF3CB115A14DF892FEA79BD776BBF
acb20554d68465b3b3119363102d14b65d6cb977835b7e7ad02aa3aa0c6cad56
'''

from PIL import Image
import argparse
import os

default_output = os.path.join(os.getcwd(), 'output.bin')

parser = argparse.ArgumentParser(prog = 'stego', description = 'stego imgs routine')
parser.add_argument('path', help = 'target file path')
parser.add_argument('-e', action='store_true', help = 'file to img')
parser.add_argument('-d', action='store_true', help = 'img to file')
parser.add_argument('-o', '--output_filename', help = 'output filename')
parser.add_argument('-w', '--width', help = 'img width')
parser.add_argument('-ht', '--height', help = 'img height')
args = parser.parse_args()

'''
Оригинальный алгоритм на C# выглядел так:

Bitmap bm = resources.GetObject("DE") as Bitmap;
int i = 0;
for (int x = 0; x < 35328; x++)
{
	for (int y = 0; y < bm.Height; y++)
	{
		for (int r = 0; r < 1; r++)
		{
			for (int c = 0; c < 1; c++)
			{
				byte red = bm.GetPixel(x + r, y + c).R;
				b[i] = red;
				i++;
			}
		}
	}
}
'''

def img_to_file():
    try:
        img = Image.open(args.path)
        width, height = img.size
        red_pixels = []

        for x in range(0, width):
            for y in range(0, height): 
                color = img.getpixel((x,y)) # RGB
                red_pixels.append(color[0]) # R - 0, G - 1, B - 2

        red_pixels_br = bytearray(red_pixels)

        output = args.output_filename if args.output_filename else default_output

        with open(output, 'wb') as f:
            f.write(red_pixels_br)
    except Exception as err:
        print(f"{err=}, {type(err)=}")
        raise
    finally:
        print('\ndecrypt done\n')
        
'''
Превращает вредоносный файл в картинку. Может использоваться в сценарии, когда 
вы пропатчили вредоносный файл, и хотите обратно закодировать его в картинку,
чтобы малварь в процессе своей работы расшифровала ваш пропатченный бинарник.
Ширину и высотву картинки надо брать такую же как в оригинале.
Для образца acb20554d68465b3b3119363102d14b65d6cb977835b7e7ad02aa3aa0c6cad56:  size=(35328, 1))
Для других образцов данный алгоритм придется модифицировать
'''


def file_to_img():
    try:
        if args.width is None or args.height is None:
            raise Exception("you must provide width and height values")
        img = Image.new(mode="RGB", size = (int(args.width), int(args.height)))

        ba = []
        with open(args.path, 'rb') as f:
            ba = bytearray(f.read())

        i = 0
        for b in ba:
            xy = (i, 0)
            value = (b, 0, 0)
            img.putpixel(xy, value)
            i += 1
        
        output = args.output_filename if args.output_filename else default_output
        img.save(output, 'BMP')
    except Exception as err:
        print(f"{err=}, {type(err)=}")
        raise
    finally:
        print('\nencrypt done\n')


        
if args.e:
    file_to_img()
elif args.d:
    img_to_file()
else:
    print("You must pass \"-e\" (encrypt) or \"-d\" (decrypt)")