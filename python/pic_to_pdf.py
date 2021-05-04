from PIL import Image
from argparse import Namespace, ArgumentParser

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="File of a picture.", required=True)

    args = parser.parse_args(None)

    return args

def main():
    args = get_args()

    img = Image.open(args.file)
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # remove extension from filename and put 'pdf' there
    result_filename = '{}.pdf'.format(
        '.'.join(
            args.file.split('.')[:-1]
        )
    )
    img.save( result_filename )

if __name__ == "__main__":
    main()