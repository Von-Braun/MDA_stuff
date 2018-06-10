import sys; from PIL import Image; import numpy as np
import time,os,random,string
import serial
import collections

serl = serial.Serial('COM3', 115200) # Establish the connection on a specific port
time.sleep(2)
def print_arduino(string_to_use):
    #string_to_use="hello\ntest1\ntest2"#.replace('\n','\\n\n')
    #for line in :
    serl.write(string_to_use+' ')#.replace('\n',''))
        #time.sleep(.1)


ASCII_CHARS = [ '#', '?', '%', '.', 'S', '+', '.', '*', ':', ',', '@']
ASCII_CHARS = [ '#', '@', '&', '$', '?', '!', '+', '-', ',', '.', ' '][::-1]
#ASCII_CHARS = [ '@', '8', '0', 'G', 't', 'i', ';', ':', ',', '.',' '][::-1]
greyscale = [
            " ",
            " ",
            ".,-",
            "_ivc=!/|\\~",
            "gjez2]/(YL)t[+T7Vf",
            "mdK4ZGbNDXY5P*Q",
            "W8KMA",
            "#%$"
            ]
set_width=25

def scale_image(image, new_width=set_width):
    """Resizes an image preserving the aspect ratio.
    """
    (original_width, original_height) = image.size
    aspect_ratio = original_height/float(original_width)
    new_height = int(aspect_ratio * new_width)

    new_image = image.resize((new_width, new_height))
    #print 'Width:',new_width*2,'  Hight:',new_height
    return new_image,new_width,new_height

def convert_to_grayscale(image):
    return image.convert('L') # convert to mono

def map_pixels_to_ascii_chars(image, range_width=25):
    """Maps each pixel to an ascii char based on the range
    in which it lies.

    0-255 is divided into 11 ranges of 25 pixels each.
    """

    pixels_in_image = list(image.getdata())
    pixels_to_chars = [ASCII_CHARS[pixel_value/range_width]*2 for pixel_value in pixels_in_image]
    #pixels_to_chars = [random.choice(greyscale[pixel_value/range_width])*2 for pixel_value in pixels_in_image]
            

    return "".join(pixels_to_chars)

def convert_image_to_ascii(image, new_width=set_width):
    test_width=100
    test_hight=100
    start_width=81
    image_to_convert=image
    #image = scale_image(image_to_convert)[0]
    #"""
    while test_hight>25 or (test_width*2)>79:
        image = scale_image(image_to_convert,start_width)
        test_width=image[1]
        test_hight=image[2]
        start_width-=1
    new_width=test_width*2
    image=image[0]
    #"""
    image = convert_to_grayscale(image)

    pixels_to_chars = map_pixels_to_ascii_chars(image)
    len_pixels_to_chars = len(pixels_to_chars)

    image_ascii = [pixels_to_chars[index: index + new_width] for index in
            xrange(0, len_pixels_to_chars, new_width)]

    return "\n".join(image_ascii)

def pad_image(provided_image_ascii):
    edge_charecters=''
    image_width=0
    for line in provided_image_ascii.split('\n'):
        edge_charecters+=line[:1]+line[-1:] #append first and last charecter
    image_width=len(line)
    print 5

    most_common_char = collections.Counter(edge_charecters).most_common(1)[0][0]
    new_image = []
    space_left=(79-image_width)/2
    for line in provided_image_ascii.split('\n'):
        new_image.append(  (most_common_char*space_left)+line+(most_common_char*space_left)  )
    return '\n'.join(new_image)

def handle_image_conversion(image_filepath):
    from PIL import Image
    image = Image.open(image_filepath)
    image.seek(0) # skip to the second frame

    try:
        while 1:
            
            os.system('cls')
            image_ascii = convert_image_to_ascii(image)
            image_ascii = pad_image(image_ascii)
            print_arduino(image_ascii)
            print image_ascii
            time.sleep(.04)
            image.seek(image.tell()+1)
    except EOFError:
        print 'Dead'
        pass # end of sequence
    
    

if __name__=='__main__':
    import sys

    image_file_path = sys.argv[1]
    while True:
        handle_image_conversion(image_file_path)
