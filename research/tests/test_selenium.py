from django.test import TestCase
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
import time


class ResearchFormTest(TestCase):

    def setUp(self):
        self.selenium = Firefox()
        # url to visit
        self.selenium.get('http://127.0.0.1:8000/')

    def tearDown(self):
        self.selenium.close()

    def test_research_if_keywords_match(self):
        # find the elements you need to submit form
        researched_food_keywords = self.selenium.find_element_by_id('id_research')

        submit = self.selenium.find_element_by_id('submit_research')

        # populate the form with data
        keywords = 'Pizza'
        researched_food_keywords.send_keys(keywords)

        # submit form
        submit.send_keys(Keys.RETURN)

        time.sleep(10)

        # check result; page source looks at entire html document
        assert 'Vous avez saisi : ' + keywords in self.selenium.page_source

    def test_research_if_keywords_dont_match(self):
        # find the elements you need to submit form
        researched_food_keywords = self.selenium.find_element_by_id('id_research')

        submit = self.selenium.find_element_by_id('submit_research')

        # populate the form with data
        keywords = 'çeuhrgpueyrh'
        researched_food_keywords.send_keys(keywords)

        # submit form
        submit.send_keys(Keys.RETURN)

        time.sleep(10)

        # check result; page source looks at entire html document
        assert "Aucun aliment ne correspond à votre recherche..." in self.selenium.page_source
