#path manipulation, making directory, globbing only images
import os
from glob import glob
from pathlib import Path

#parse arguments
import argparse

#image manipulation
from PIL import Image

#saving to RAM instead of disk
from io import BytesIO

#image quality bounds
LOWEST_QUALITY = 20
HIGHEST_QUALITY = 100

def save_image_64kb(image, path, buffer):
    #try to get 64kb or less
    low = LOWEST_QUALITY
    high = HIGHEST_QUALITY

    while low<high:
        mid = low+high
        #bit shift with cieling
        mid = (mid>>1) + (mid & 1)

        #try saving with quality

        #go back to buffer start
        buffer.seek(0)
        #save to buffer
        image.save(buffer,'JPEG', quality = mid)
        #get the location in the buffer after save
        img_size = buffer.tell()

        #check if size is less than 64kb
        if img_size<= 64e3:
            print('found',mid,img_size)
            low = mid
        else:
            high=mid-1
    
    image.save(path,'JPEG', quality= low)

    if(os.stat(path).st_size > 64e3):
        print('failed to save lower than 64kb')
        
def parse_args():
    #argparse get path
    parser = argparse.ArgumentParser(description= 'Resize images in bulk from directory')
    parser.add_argument('path',type=str, metavar='path/to/dir/',nargs='?', default='./',
        help='directory containing the folders, defaults to cwd'
    )
    return parser.parse_args()

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
    with BytesIO() as buf:
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
            save_image_64kb(new_image, new_image_dir / new_image_path,buffer=buf)


if __name__ == "__main__":
    path = parse_args().path

    #check path validity
    if os.path.isdir(path):
        os.chdir(path)
        main()
    else:
        raise OSError('not a directory')