import os
from sklearn.model_selection import train_test_split

from lxml import etree
import pandas as pd


class Cocktail(object):
    def __init__(self, name=None, ingredients=None, ingredients_quantity_unit=None, ingredients_by_taxonomy=None, preparation=None):
        self.name = name
        self.ingredients = [ingredient.lower() for ingredient in ingredients]
        self.ingredient_quantity_unit = [("", "") for _ in ingredients] if ingredients_quantity_unit is None else [(c, u) if c != '0' else ("", "") for (c, u) in ingredients_quantity_unit]
        self.ingredients_by_taxonomy = ingredients_by_taxonomy
        self.preparation = preparation
        self.taxonomy_types = self._get_taxonomy_types()
        self.penalty = 0

    def _get_taxonomy_types(self):
        types = []
        for key, ingredients in self.ingredients_by_taxonomy.items():
            if len(ingredients) != 0:
                types.append(key)
        return types


class CaseBase(object):
    def __init__(self, cocktail_file='ccc_cocktails.xml', taxonomy_file='app/taxonomy_taste.csv', penalty_step=0.1, train_ratio=0.8, random_state=42):
        self.cocktail_file = cocktail_file
        self.taxonomy_file = taxonomy_file
        self.train_ratio = train_ratio
        self.random_state = random_state
        self.penalty_step = penalty_step
        self.id = 1

        self.all_ingredients, self.all_ingredients_by_taxonomy = self._get_all_ingredients()
        names_train, names_test = self._split_data()
        self.cocktails, self.cocktails_test = self._get_cocktails(names_train, names_test)
        self.w = self._get_taxonomy_weights()

    def add_cocktail(self, cocktail, name):
        cocktail.name = str(self.id) + '_' + name
        self.id += 1
        if cocktail.name not in self.cocktails:
            self.cocktails[cocktail.name] = cocktail

    def penalize_cocktail(self, cocktail_name):
        self.cocktails[cocktail_name].penalty = min(self.cocktails[cocktail_name].penalty + self.penalty_step, 1)

    def get_sim_cocktails(self, query_cocktail):
        taxonomy_attributes = list(self.all_ingredients_by_taxonomy.keys())
        cocktails_with_sim = {}

        for cocktail_name in self.cocktails.keys():
            cocktail = self.cocktails[cocktail_name]
            sim_taxonomy = self._jaccard_distance(cocktail.taxonomy_types, query_cocktail.taxonomy_types)
            sim_ingredients = 0
            sum_w = 0
            for att in taxonomy_attributes:
                sim_ingredients += self.w[att] * self._jaccard_distance(cocktail.ingredients_by_taxonomy[att], query_cocktail.ingredients_by_taxonomy[att])
                if len(cocktail.ingredients_by_taxonomy[att]) != 0 or len(query_cocktail.ingredients_by_taxonomy[att]) != 0:
                    sum_w += self.w[att]

            sim_cocktail = (1 - cocktail.penalty) * (0.75 * sim_taxonomy + 0.25 * (sim_ingredients / sum_w))
            cocktails_with_sim[cocktail] = (sim_cocktail, cocktail.name)

        return cocktails_with_sim

    def retrieve_cocktails(self, cocktails_with_sim, k_top):
        titles_sort = sorted(cocktails_with_sim, key=lambda x: cocktails_with_sim[x][0], reverse=True)[0:k_top]
        cocktails_retrieved = {}
        for title in titles_sort:
            cocktails_retrieved[title] = cocktails_with_sim[title]
        return cocktails_retrieved

    def save_xml(self, file_name):
        f = open(file_name, "w")
        print("<?xml version=\"1.0\"?>", file=f)
        print("<recipes>", file=f)
        for name, cocktail in self.cocktails.items():
            recipe = ("\t<recipe>" + '\n')
            recipe += ("\t\t<title>" + name + "</title>" + '\n')
            recipe += ("\t\t<ingredients>" + '\n')
            for i, (q, u) in zip(cocktail.ingredients, cocktail.ingredient_quantity_unit):
                recipe += ("\t\t\t<ingredient quantity=\"" + q + "\" unit=\"" + u + "\" food=\"" + i + "\">" + " ".join([q, u, i]) + "</ingredient>" + '\n')
            recipe += ("\t\t</ingredients>" + '\n')
            recipe += ("\t\t<preparation>" + '\n')
            for i in cocktail.preparation:
                recipe += ("\t\t\t<step>" + i.strip().capitalize() + "</step>" + '\n')
            recipe += ("\t\t</preparation>" + '\n')
            recipe += ("\t\t<penalty>" + str(cocktail.penalty) + "</penalty>" + '\n')
            recipe += "\t</recipe>"
            print(recipe, file=f)
        print("</recipes>", file=f)
        f.close()

    def _split_data(self):
        names = self._get_cocktail_names()
        names_train, names_test = train_test_split(names, train_size=self.train_ratio, random_state=self.random_state)
        return names_train, names_test

    def _get_taxonomy_weights(self):
        w = {}
        total_ingredients = sum([len(self.all_ingredients_by_taxonomy[key]) for key in self.all_ingredients_by_taxonomy.keys()])
        for att in self.all_ingredients_by_taxonomy.keys():
            total_ingredients_att = len(self.all_ingredients_by_taxonomy[att])
            w[att] = total_ingredients_att / total_ingredients
        return w

    @staticmethod
    def _jaccard_distance(ingredients_cocktail, ingredients_default):
        I = set(ingredients_cocktail).intersection(set(ingredients_default))
        U = set(ingredients_cocktail).union(set(ingredients_default))
        if len(U) == 0:
            return 0
        else:
            return len(I) / len(U)

    @staticmethod
    def _init_taxonomy_dict():
        taxonomy_dict = {
            'spicy': [],
            'fresh': [],
            'sweet': [],
            'salty': [],
            'dry': [],
            'warm': [],
            'gassed': [],
            'acid': [],
            'bitter': [],
            'others': [],
            'alcohol': [],
            'fruit': [],
            'juice': [],
            'syrup': []}
        return taxonomy_dict

    def _get_cocktail_names(self):
        tree = etree.parse(self.cocktail_file)
        root = tree.getroot()
        titles = root.findall('recipe/title')
        names = [title.text for title in titles]
        return names

    def _get_all_ingredients(self):
        self.taste_taxonomy = pd.read_csv(self.taxonomy_file, header=0)
        tree = etree.parse(self.cocktail_file)
        root = tree.getroot()
        ingredient_names = root.findall('recipe/ingredients/ingredient')
        ingredients_list = []
        ingredients_by_taxonomy_dict = self._init_taxonomy_dict()
        for i in ingredient_names:
            ingredient = i.get('food').lower()
            if ingredient not in ingredients_list:
                ingredients_list.append(ingredient)
                for att in self.taste_taxonomy.columns:
                    if ingredient in self.taste_taxonomy[att].values:
                        ingredients_by_taxonomy_dict[att].append(ingredient)
        return ingredients_list, ingredients_by_taxonomy_dict

    def get_taxonomy(self, ingredients):
        if isinstance(ingredients, list):
            taxonomy = self._init_taxonomy_dict()
            for att in self.taste_taxonomy.columns:
                for ingredient in ingredients:
                    if ingredient in self.taste_taxonomy[att].values:
                        taxonomy[att].append(ingredient)
        else:
            taxonomy = []
            for att in self.taste_taxonomy.columns:
                if ingredients in self.taste_taxonomy[att].values:
                    taxonomy.append(att)

        return taxonomy

    def get_cocktail(self, cocktail_name):
        if cocktail_name in self.cocktails:
            return self.cocktails[cocktail_name]
        return None

    def _get_cocktails(self, names_train, names_test):
        taste_taxonomy = pd.read_csv(self.taxonomy_file, header=0)
        tree = etree.parse(self.cocktail_file)
        root = tree.getroot()
        cocktails_train = {}
        cocktails_test = {}
        for recipe in root.findall('recipe'):
            cocktail_name = recipe.find('title').text
            ingredients = recipe.find('ingredients')
            cocktail_ingredients = []
            cocktail_ingredients_quantity_unit = []
            cocktail_ingredients_by_taxonomy = self._init_taxonomy_dict()
            for ingredient in ingredients:
                ing_name = ingredient.attrib['food'].lower()
                ing_quantity = ingredient.attrib['quantity']
                ing_unit = ingredient.attrib['unit']
                cocktail_ingredients.append(ing_name)
                cocktail_ingredients_quantity_unit.append((ing_quantity, ing_unit))
                for att in taste_taxonomy.columns:
                    if ing_name in taste_taxonomy[att].values:
                        cocktail_ingredients_by_taxonomy[att].append(ing_name)

            preparation = recipe.find('preparation')
            cocktail_preparation = []
            for step in preparation:
                s = step.text.lower().replace('.}}', '').replace('[', '').replace(']', '').replace("}}", '').replace('}}', '')
                cocktail_preparation.append(s)

            cocktail = Cocktail(cocktail_name, cocktail_ingredients, cocktail_ingredients_quantity_unit, cocktail_ingredients_by_taxonomy, cocktail_preparation)
            if cocktail_name in names_train:
                cocktails_train[cocktail_name] = cocktail
            elif cocktail_name in names_test:
                cocktails_test[cocktail_name] = cocktail
        return cocktails_train, cocktails_test
