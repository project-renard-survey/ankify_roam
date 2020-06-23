import unittest
import json
import logging
from ankify_roam import roam, anki
from ankify_roam.tests.roam_export import ROAM_JSON
from ankify_roam.default_models import ROAM_BASIC, ROAM_CLOZE
from ankify_roam.ankifiers import RoamGraphAnkifier

class TestRoamGraphAnkifier(unittest.TestCase):
    def setUp(self):
        self.profile="test"
        self.deck="test"
        if not anki.load_profile(self.profile):
            raise ValueError("You need an anki profile called 'test' to run the Ankifier tests on")
        anki.delete_deck(self.deck)
        anki.create_deck(self.deck)

    def test_ankify(self):
        pages = json.loads(ROAM_JSON)
        roam_graph = roam.RoamGraph(pages)
        ankifier = RoamGraphAnkifier(deck=self.deck)
        with self.assertLogs() as ctx:
            ankifier.ankify(roam_graph)
        self.assertFalse([r for r in ctx.records if r.levelno >= logging.WARNING])

    #def test_setup_models(self):
    #    ankifier.setup_models()
    #    model_names = ROAM_BASIC['modelName'], ROAM_CLOZE['modelName']
    #    self.assertTrue(set(model_names).issubset(anki.get_model_names()))

if __name__=="__main__":
    unittest.main()