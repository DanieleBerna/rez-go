import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(prog="redrez")

    subparsers = parser.add_subparsers(help='Modes', dest='mode', required=True)
    parser_install = subparsers.add_parser('install', help='Create a new rez setup in the local folder')

    parser_install.add_argument("-m", "--map", action="store", type=str, dest="unit",
                        help="Map the local folder to another disk unit during the install process")

    parser_install.add_argument("-r", "--release", action="store", type=str, dest="release_folder",
                        help="Set a remote folder as release_packages_path")

    parser_pack = subparsers.add_parser('pack', help='Pack the existing rez given the local folder in a zip file')

    parser_deploy = subparsers.add_parser('deploy', help='Unpack and deploy to the local folder a previously zipped rez')

    parser_deploy.add_argument("-m", "--map", action="store", type=str, dest="unit",
                                help="Map the local folder to another disk unit during the install process")

    parser_deploy.add_argument("-r", "--release", action="store", type=str, dest="release_folder",
                                help="Set a remote folder as release_packages_path")

    parser.add_argument("local_folder", type=str,
                          help="rez local folder")

    args = parser.parse_args()

    if args.mode == "install":
        print(f"install and map to {args.local_folder} and map to {args.unit}")

    if args.mode == "pack":
        print(f"Pack stuff contained in {args.local_folder}")

    if args.mode == "deploy":
        print(f"Unpack zip content to {args.local_folder} and map to {args.unit}")


parse_arguments()
