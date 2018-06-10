from PIL import Image,ImageSequence
import time,os,sys,io,imageio,serial 

countv=0
background=0
img_selected=None
inverted=0
mode=1
dithered=-1

def conbyte(bytearray2use):
    global inverted
    #[255,255,0,0,0,0,0,255]
    new_bytearray2use=[]
    one='0'
    zero='1'
    if inverted:
        one='1'
        zero='0'
    for i in bytearray2use:
        if i==255:
            new_bytearray2use.append(zero)
        else:
            new_bytearray2use.append(one)
    #bytearray2use=''.join(bytearray2use.replace(0,'0').replace(255,'255'))
    return_letter = chr(int(''.join(new_bytearray2use),2))
    #if return_letter==chr(10):
    #    return_letter=chr(9)
    #if return_letter==chr(0):
    #    return_letter=chr(1)
    return return_letter

def print_arduino(image_for_arduino):
    #imgByteArr = io.BytesIO()
    #image_for_arduino.save(imgByteArr, format='BMP')
    #imgByteArr = imgByteArr.getvalue()[14:]

    count=0
    print 'Beginning pixel transformations'
    pixels = list(image_for_arduino.getdata())
    width, height = image_for_arduino.size
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    pixel_bytes=[]
    for I in range(0,height):
        for i in range(0,len(pixels[I]),8):
            count+=1
            pixel_bytes.append(conbyte(pixels[I][i:i+8]))
    print count
    print '    pixel transformations complete!'

    #print imgByteArr
    #proof = Image.open(io.BytesIO(imgByteArr))
    #proof.show()
    #print '\n',len(imgByteArr)
    #imgByteArr=bytearray(imgByteArr)
    #imgByteArr+='1'
    #for I in range(0,1):
        #for i in range(0,len(pixels[I]),8):
            #print pixels[I][i:i+8],'\n----------------------------------------------------\n'
            #serl.write(pixels[I][i:i+8])
    #serl.write(('F'*300)+'1')
    #pixel_bytes[-1:]='\n'
    print pixel_bytes.count(chr(10)),pixel_bytes.count(chr(0))
    print 'beggining loop'
    start_time = time.time()
    for i in range(0,31320,7830):
        print '    calculating string'
        newlist=''.join(pixel_bytes[i:i+7830])#+chr(10)
        print '        calculated\nsending!'
        #newlist.append('\n')
        serl.write(newlist)
        print '    sent!\nwaiting'
        time.sleep(0.2)
        print '    waiting complete',time.time() - start_time
    #print len(chr(255)*31320)
    #print serl.write((chr(255)*31320)+'\n')

def scale_image(image,new_width):
    """Resizes an image preserving the aspect ratio.
    """
    (original_width, original_height) = image.size
    aspect_ratio = original_height/float(original_width)
    new_height = int(aspect_ratio * new_width)

    new_image = image.resize((new_width, new_height))
    #print 'Width:',new_width*2,'  Hight:',new_height
    return new_image,new_width,new_height

def convert_to_grayscale(image):
    if dithered!=-1:
        gray = image.convert('L') # convert to black and white
        return gray.point(lambda x: 0 if x<int(dithered) else 255, '1')
    else:
        return image.convert('1')

def convert_image_to_ascii(image, new_width=720):
    global background
    test_width=721
    test_hight=349
    start_width=720
    image_to_convert=image
    while test_hight>348 or test_width>720:
        image = scale_image(image_to_convert,start_width)
        test_width=image[1]
        test_hight=image[2]
        start_width-=1
    image = convert_to_grayscale(image[0]) #convert to black/white
    canvas = Image.new("1", (720, 348), 255*background)
    canvas.paste(image,((720-test_width)/2,(348-test_hight)/2))
    #canvas.show()
    return canvas

def handle_image_conversion():
    global countv, mode
    from PIL import Image
    image_array=[]

    if img_selected==None:
        print 'Warning: no image provided. Creating blank image instead'
        blank_screen = Image.new("1", (720, 348), 255*background)    
        if mode==0:
            print_arduino(blank_screen)
            time.sleep(.04)
        elif mode==1:
            file_name = 'temp.gif'
            blank_screen.save(file_name)
            image_array.append(imageio.imread(file_name))
            print 'Saving Image...'
            os.remove(file_name) 
            imageio.mimsave('test.gif', image_array)
            print 'Done'
        return

    image = Image.open(img_selected)
    frames = [frame.copy() for frame in ImageSequence.Iterator(image)]
    for im in frames:
        print 'Frame: '+str(frames.index(im)+1)+'/'+str(len(frames))+', '+str(countv)+'\r',
        
        image_graphic = convert_image_to_ascii(im)
        if mode==0:
            print_arduino(image_graphic)
            time.sleep(.04)
        elif mode==1:
            file_name = 'temp.'+img_selected.split('.')[1]
            image_graphic.save(file_name)
            image_array.append(imageio.imread(file_name))

    if mode==1:
        print '\nSaving Image...'
        os.remove(file_name) 
        imageio.mimsave('test.gif', image_array)
        print 'Done'

def handle_arguments():
    global background, img_selected, inverted, dithered, mode
    #sys.argv = ['graphicsw','-B0','-I1','-D123','test.jpg']
    arguments = sys.argv[1:]
    completed_arguments=[]
    
    if len(arguments)==0:
        print 'Warning: no arguments provided! Type <program> -h for help'  
    elif '-h' in arguments:
        return True

    for i in arguments:
        if i[0:2]=='-b' and (i[2:3]=='0' or i[2:3]=='1') and ('b' not in completed_arguments):
            background=int(i[2:3])
            completed_arguments.append('b')

        elif i[0:2]=='-i' and (i[2:3]=='0' or i[2:3]=='1') and ('i' not in completed_arguments):
            inverted=int(i[2:3])
            completed_arguments.append('i')

        elif i[0:2]=='-a' and (i[2:3]=='0' or i[2:3]=='1') and ('a' not in completed_arguments):
            mode=int(i[2:3])
            completed_arguments.append('a')

        elif i[0:2]=='-d' and i[2:].isdigit() and 0<=int(i[2:])<=255 and ('d' not in completed_arguments):
            dithered=int(i[2:])
            completed_arguments.append('d')

        elif 'g' not in completed_arguments:
            img_selected=i
            completed_arguments.append('g')

        else: 
            return True
    return False
            

if __name__=='__main__':
    failed = handle_arguments()
    if not failed:

        if mode==0:
            serl = serial.Serial('COM3', 2000000) # Establish the connection on a specific port
            #time.sleep(2)
            #serl.write(chr(1))
            time.sleep(2)
        #while not mode:
        #    handle_image_conversion(image_file_path,white_limit)
        handle_image_conversion()
        countv+=1
    else:
        print 'format:  graphicsw -a<1/0> -b<1/0> -i<1/0> -d<0-255> <image name>\n'
        print 'a   ....  save option(0=arduino,1=file[DEFAULT])'
        print 'img ....  image selected(blank screen if none provided)'
        print 'i   ....  invert image? (1=invert image, 0=don\'t invert[DEFAULT])'
        print 'b   ....  background colour (0=black[DEFAULT], 1=white)'
        print 'd   ....  dithered? (blank=dither[DEFAULT], else white select with no dither)\n'
        print 'example1: graphicsw -b0 -i1 -d123 test.jpg'
        print 'example2: graphicsw -d80 test23.gif -i0\n'     
