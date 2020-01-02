import os
import argparse
from PIL import Image
from glob import glob
from pathlib import Path

LOWEST_QUALITY = 20

def save_image_16kb(image, path):
    #try to get 16kb or less

    #max quality
    quality = 95

    while True:
        #try saving with quality
        image.save(path, quality = quality)

        #check if size is less than 16kb
        if os.stat(path).st_size <= 64e3:
            break
        elif quality == LOWEST_QUALITY:
            print('Failed to get {path} to 16kb or less'.format(path=path))
            break
        else:
            os.remove(path)
            quality = (LOWEST_QUALITY + quality) >> 1
        
    


def main():
    files = []
    for ext in ('*.png','*.jpg'):
        files.extend(glob(ext))

    #make the destination directory and change dir
    try:
        os.mkdir('new_images')
    except:
        pass
    
    new_image_dir = Path('new_images')

    for image_path in files:
        
        #rename as .jpg
        image_name, ext = os.path.splitext(image_path)
        new_image_path = image_name + '.jpg'
        
        #load image
        image = Image.open(image_path)

        #get the new width and height        
        width, height = image.size
        #ratio*width,
        #ratio*height <= ratio*max(width,height) =400
        #and the greater multiplied by the ratio is 400
        ratio = 400/max(width,height)
        new_width, new_height = round(width*ratio), round(height*ratio)

        #make resized image
        new_image = image.resize((new_width, new_height), Image.ANTIALIAS)

        #check if image has alpha channel, since in that case it can't be saved as jpg
        #https://pillow.readthedocs.io/en/4.0.x/handbook/concepts.html
        if new_image.mode in ('RGBA','LA'):
            new_image = new_image.convert('RGB')
        
        #try to save image in 16kb or less
        save_image_16kb(new_image, new_image_dir / new_image_path)


if __name__ == "__main__":
    
    #argparse get path
    parser = argparse.ArgumentParser('Resize images in bulk from directory')
    parser.add_argument('path',type=str, metavar='path/to/dir/',nargs='?', default='./',
        help='directory containing the folders, defaults to cwd'
    )
    path = parser.parse_args().path

    #check path validity
    if os.path.isdir(path):
        os.chdir(path)
        main()
    else:
        raise OSError('not a directory')