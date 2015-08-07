# This script is an example of how you can run blender from the command line
# (in background mode with no interface) to automate tasks, in this example it
# creates a text object, camera and light, then renders and/or saves it.
# This example also shows how you can parse command line options to scripts.
#
# Example usage for this test.
#  blender --background --factory-startup --python $HOME/background_job.py -- \
#          --text="Hello World" \
#          --render="/tmp/hello" \
#          --save="/tmp/hello.blend"
#
# Notice:
# '--factory-startup' is used to avoid the user default settings from
#                     interfearing with automated scene generation.
#
# '--' causes blender to ignore all following arguments so python can use them.
#
# See blender --help for details.

import bpy
import os

def get_name_pattern(name, token='#'):
    """Get a string's padding pattern"""
    
    l = ['']
    
    last_isdigit = name[0].isdigit()
    
    for c in name:
        if last_isdigit == c.isdigit():
            l[-1]+=c
        else:   
            l.append(c)
            
            last_isdigit = not last_isdigit
        
    
    for i in range(len(l)-1, -1, -1):
        if l[i][0].isdigit():
            l[i] = token #* len(l[i])
            break
    
    
    out = ''.join(l)
    return out

def get_frame_number(name, token='#'):
    """TODO: avoid duplicate function?"""
    
    l = ['']
    
    last_isdigit = name[0].isdigit()
    
    for c in name:
        if last_isdigit == c.isdigit():
            l[-1]+=c
        else:   
            l.append(c)
            
            last_isdigit = not last_isdigit

    for i in range(len(l)-1, -1, -1):
        if l[i][0].isdigit():
            return int(l[i])
            
def padding(s, frame):
    """Get frame's final name from expression"""

#    if not '#' in s:
#        s += '{:04}'.format(frame)

    out = ''
    pad = 0
    for c in s + '_':
        if c != '#':
            
            if pad != 0:
                num = ('{:0' + str(pad) + '}').format(frame)
                out += num
            
                pad = 0
            out +=c
        else:
            pad += 1
    
    out = out[0:-1]
    if not '#' in os.path.basename(s):
        out = '{}{:04}'.format(out,frame)
    return out

def add_text(sequencer, text, position, channel, frame, font_color=[1.0,1.0,1.0]):
    #TODO: BG
    #

    # deselect all
    for s in sequencer.sequences:
        s.select = False


    txt_seq = sequencer.sequences.new_effect('{}_f{:04}'.format(text, frame), 'TEXT', channel, frame+1, frame+2)
    txt_seq.text = text
    # txt_seq.blend_type = 'OVER_DROP'
    txt_seq.location = position

    txt_seq = sequencer.sequences.new_effect('{}_f{:04}_BG'.format(text, frame), 'COLOR', channel+1, frame+1, frame+2)
    txt_seq.color = font_color
    txt_seq.blend_type = 'MULTIPLY'
    # txt_seq.location = position

    bpy.ops.sequencer.meta_make()
    meta = sequencer.active_strip
    meta.blend_type = 'OVER_DROP'


def render_stamp(images_paths, text, render_dir):

    scene = bpy.context.scene
    sequencer = scene.sequence_editor_create()
    

    # Get images using same pattern in dir
    if len(images_paths) == 1:
        imgs = []
        img_dir, img_name = os.path.split(images_paths[0])
        pattern = get_name_pattern(img_name)
        file_list = os.listdir(img_dir)
        for f in file_list:
            if get_name_pattern(f) == pattern:
                imgs.append(os.path.join(img_dir, f))
        images_paths = imgs
        images_paths.sort(key=get_frame_number)


    img_seq = sequencer.sequences.new_image('img', images_paths[0], 1, 1)


    for i in images_paths[1:]:
        img_seq.elements.append(os.path.basename(i))


    # Scene options
    scene.frame_end = img_seq.frame_final_duration

    img_seq.update()
    scene.update()


    # Get image size
    img = bpy.data.images.load(images_paths[0])
    print(list(img.size))
    # print(img_seq.elements[0].filename)
    # print('resolution:', img_seq.elements[0].orig_width, img_seq.elements[0].orig_height)

    scene.render.resolution_x = img.size[0]
    scene.render.resolution_y = img.size[1]

    # scene.render.resolution_x = img_seq.elements[0].orig_width
    # scene.render.resolution_y = img_seq.elements[0].orig_height
    scene.render.resolution_percentage = 100
    
    scene.render.filepath = '//machin'

    if bpy.app.build_options.codec_ffmpeg:
        scene.render.image_settings.file_format = 'H264'
        scene.render.ffmpeg.format = 'QUICKTIME'

    scene.render.filepath = render_dir
    print(render_dir)


    for f in range(len(images_paths)):
        add_text(sequencer, 'Frame: {:04}'.format(f), [0.5, 0.0], 2, f, [0,0,1])
        # txt_seq = sequencer.sequences.new_effect('txt_{:04}'.format(f), 'TEXT', 2, f+1, f+2)
        # txt_seq.text = text + ' {:04}'.format(f+1)
        # txt_seq.blend_type = 'OVER_DROP'

    bpy.ops.render.render(animation=True)


def main():
    """Parse arguments"""

    import sys       # to get command line args
    import argparse  # to parse options for us and print a nice help message

    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # print('    INSIDE ARGS:', argv)
    # print('    INSIDE FILE:', os.path.abspath(__file__))
    # When --help or no args are given, print this help

    usage_text = \
    """Select images to add to sequence and arguments for metadata"""
      # stamp.py --background --python """ + os.path.basename(__file__) + """ -- [options]"""

    parser = argparse.ArgumentParser(description=usage_text, prog="stamp.py")

    # Example utility, add some text and renders or saves it (with options)
    # Possible types are: string, int, long, choice, float and complex.
    parser.add_argument("image", nargs='+', type=str, help="Path to an image")

    # parser.add_argument("-t", "--text", dest="text",
    #         help="Text to write")

    parser.add_argument("-o", "--out", dest="render_dir", metavar='PATH',
            help="Render sequence to the specified path")


    metas = [
        ["date",       "-d", "--date",       "Date of creation"],
        ["author",     "-a", "--author",     "Author"],
        ["project",    "-p", "--project",    "Project"],
        ["shot",       "-s", "--shot",       "Shot"],
        ["sequence",   "-S", "--sequence",   "Sequence"],
        ["focal",      "-f", "--focal",      "Focal"],
        ["rendertime", "-r", "--rendertime", "Render time"],
        ["text",       "-t", "--text",       "Custom text"]
    ]

    for m in metas:
        parser.add_argument(m[1], m[2], dest=m[0],
            help=m[3])

    print('\n')
    args = parser.parse_args(argv)  # In this example we wont use the args

    if not argv:
        parser.print_help()
        return

    if not args.image:
        print("Error: image argument not given, aborting.")
        parser.print_help()
        return

    if not args.render_dir:
        args.render_dir = os.path.dirname(args.image[0]) + os.path.sep

    # Run the example function
    render_stamp(args.image, args.text, args.render_dir)
    print("batch job finished, exiting")



if __name__ == "__main__":
    main()