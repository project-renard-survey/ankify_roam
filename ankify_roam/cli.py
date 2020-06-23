import inspect
import argparse
from ankify_roam import anki
from ankify_roam.default_models import ROAM_BASIC, ROAM_CLOZE
from ankify_roam.ankifiers import RoamGraphAnkifier
from ankify_roam.roam import RoamGraph

logger = logging.getLogger(__name__)

def add(path, **kwargs):
    logger.info("Loading Roam Graph")
    roam_graph = RoamGraph.from_path(path)
    RoamGraphAnkifier(**kwargs).ankify(roam_graph)

def init(overwrite=False):
    modelNames = anki.get_model_names()
    for model in [ROAM_BASIC, ROAM_CLOZE]:
        if not model['modelName'] in modelNames:
            anki.create_model(model)
        else:
            if overwrite:
                anki.update_model(model)
            else:
                logging.info(
                    f"'{model['modelName']}' already in Anki. "\
                    "If you want to overwrite it, set `overwrite=True`")

def main():
    def get_default_args(func):
        signature = inspect.signature(func)
        return {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }
    parser = argparse.ArgumentParser(description='Import flashcards from Roam to Anki')
    subparsers = parser.add_subparsers(help='sub-command help')

    # initialize
    parser_init = subparsers.add_parser("init", 
        help="Initialize Anki with Roam specific models",
        description="Initialize Anki with Roam specific models")
    parser_init.add_argument('--overwrite', action="store_true", 
        help="whether to overwrite the models if they already exist")
    parser_init.set_defaults(func=init)

    # add roam to anki
    default_args = get_default_args(RoamGraphAnkifier.__init__)
    parser_add = subparsers.add_parser("add", 
        help='Add a Roam export to Anki',
        description='Add a Roam export to Anki')
    parser_add.add_argument('path',
                        metavar='path',
                        type=str,
                        help='path to the Roam export file or containing directory')
    parser_add.add_argument('--deck', default=default_args['deck'],
                        type=str, action='store', 
                        help='default deck to add notes to')
    parser_add.add_argument('--basic_model', default=default_args['basic_model'], 
                        type=str, action='store', 
                        help='default model to assign basic cards')
    parser_add.add_argument('--cloze_model', default=default_args['cloze_model'],
                        type=str, action='store', 
                        help='default model to assign cloze cards')
    parser_add.add_argument('--pageref-cloze', default=default_args['pageref_cloze'],
                        type=str, action='store', 
                        choices=["inside", "outside", "base_only"],
                        help='where to place clozes around page references')
    parser_add.add_argument('--tag-ankify', default=default_args['tag_ankify'],
                        type=str, action='store', 
                        help='Roam tag used to identify blocks to ankify')
    parser_add.set_defaults(func=add)

    args = vars(parser.parse_args())
    func = args.pop("func")
    func(**args)

if __name__=="__main__":
    main()