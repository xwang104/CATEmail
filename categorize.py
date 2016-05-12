import os
from sets import Set
import re
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")

def vocabulary (subject, body):
  content = subject + " " + body
  content = content.replace("\n", " ").replace("\r", " ").lower()
  content = re.split("[\s,.?!:;()&\/\[\]=\-\*_\\\\]+", content)
  voc = Set([])
  for i in range(len(content)):
    if len(content[i]) < 20 and content[i].isalpha():
      voc.add(stemmer.stem(content[i]))
  return voc

def document_features(document):
  label_word_features = ['coupon', 'code', 'discout', 'sale', 'deal', 'sale', 'off', 'offer', 'save', 'expire', 'end', 'up', 'free', 'gift', 'new', 'clearance', 'under', 'buy', 'purchase']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features


def document_features_food(document):
  label_word_features =  ['food', 'pizza', 'snack', 'chip', 'candy', 'chocolate', 'cheese', 'eat', 'restaurant', 'meal', 'dinner', 'steak', 'coffee', 'tea', 'wine', 'beer']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features

def document_features_clot(document):
  label_word_features =  ['look', 'dress', 'top', 'tee', 'hoodie', 'sweatshirt', 'sweater', 'jean', 'pant', 'legging', 'skirt', 'shorts', 'active', 'swimsuit', 'lingerie', 'sleep', 'lounge', 'jumpsuit', 'romper', 'overall', 'coat', 'jacket', 'parka', 'vest', 'suit', 'blazer', 'sock','shirt', 't-shirt', 'trousers', 'bottom', 'polo', 'tank', 'sweetpant', 'jogger', 'cami', 'bra', 'bralette', 'tight', 'jegging', 'stocking', 'crop', 'sleepwear', 'clothes', 'apparel', 'undie', 'denim', 'lace', 'cashmere', 'wool', 'cotton', 'fashion', 'tunic', 'outlet', 'style', 'women', 'man', 'couture', 'romper']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features

def document_features_acce(document):
  label_word_features = ['accessory','belt', 'sunglass', 'scarf', 'wrap', 'glove', 'hat', 'cap', 'earmuff', 'handbag', 'backpack', 'clutch', 'bag', 'scatch', 'tote', 'wallet', 'purse', 'wristlet', 'charm', 'glass', 'watch', 'necklace', 'ring', 'bracelet', 'bangle', 'earring', 'suitcase', 'kipling']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features

def document_features_shoe(document):
  label_word_features =  ['shoe', 'boot', 'sneaker', 'flat', 'loafer', 'slip-on', 'mule', 'clog', 'oxford', 'pump', 'sandal', 'slipper', 'heel', 'wedge']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features

def document_features_beau(document):
  label_word_features =  ['beauty', 'fragrance', 'skin', 'makeup', 'brush', 'nail', 'hair', 'body', 'bath', 'eye', 'lip', 'face', 'moisturizer', 'cleanser', 'care', 'serum', 'mask', 'sun', 'scent', 'concentrate', 'wrinkle', 'cosmetic', 'soap', 'hand', 'skincare']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features

def document_features_home(document):
  label_word_features =  ['home', 'garden','flower', 'bed', 'cook','cookware', 'pan', 'apron', 'cooker', 'container', 'storage', 'knives', 'kitchen', 'microwave', 'scale', 'pot', 'comforter', 'sheet', 'sofa', 'desk', 'chair', 'table', 'mattress', 'furniture', 'shelf', 'rack', 'drawer', 'wood', 'stainless', 'rent', 'house', 'apartment', 'rug', 'light', 'decorate', 'bulb']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features

def document_features_elec(document):
  label_word_features = ['electronic', 'monitor', 'computer', 'keyboard', 'mouse', 'cable', 'laptop', 'iphone', 'itunes', 'apple', 'google', 'android', 'charger', 'camera', 'digital', 'earphone', 'headphone', 'cellphone', 'phone', 'tablet', 'printer', 'software', 'gps', 'game', 'video', 'TV', 'music', 'photo', 'app']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features

def document_features_trav(document):
  label_word_features = ['flight', 'bus', 'taxi', 'uber', 'airline', 'ticket', 'car', 'rent', 'hotel', 'seat', 'cruise', 'travel', 'resort', 'trip', 'travel','park', 'beach', 'inn', 'lake', 'getaway', 'mile', 'relax', 'casino']
  features = {}
  for word in label_word_features:
    features['contains({})'.format(word)] = (word in document)
  return features



import pickle
f = open('classifier.pickle', 'rb')
classifier = pickle.load(f)
f.close()

def categorize_dis_trend(word_bag):
  return classifier.classify(document_features(word_bag))

classifierdir = "/home/angela_wang1989/CATEmail/classifiers"

feat_dict = {'classifier_acce.pickle': document_features_acce,
             'classifier_food.pickle': document_features_food,
             'classifier_beau.pickle': document_features_beau,
             'classifier_clot.pickle': document_features_clot,
             'classifier_elec.pickle': document_features_elec,
             'classifier_home.pickle': document_features_home,
             'classifier_shoe.pickle': document_features_shoe,
             'classifier_trav.pickle': document_features_trav
}

clas_dict = {}

for file in os.listdir(classifierdir):
  f = open("%s/%s"%(classifierdir, file), "rb")
  clas_dict[file] = pickle.load(f);
  f.close()

def categorize_product(word_bag):
  categories = []
  for name in clas_dict.keys():
    classifier = clas_dict[name]
    res = classifier.classify(feat_dict[name](word_bag))
    if res != 'other':
      categories.append(res)
  return categories

def main():
  for name in clas_dict.keys():
    print clas_dict[name].classify(feat_dict[name](Set(["food", "wine", "pizza"])))



if __name__=="__main__":
  main();

