from flask import Flask, render_template
from forms import AutomaticAnalyzeForm, ManualAnalyzeForm
import json
import re
import nltk
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder, QuadgramCollocationFinder
from nltk.tokenize.toktok import ToktokTokenizer
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '7b7e30111ddc1f8a5b1d80934d336798'


@app.route('/')
def index():
    return render_template('index.html', data=None)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    automaticForm = AutomaticAnalyzeForm()
    manualForm = ManualAnalyzeForm()
    showAutomatic = True
    data = None
    formSubmit = False
    noResults = False

    texts = None
    MAX_RESULTS = None
    NUM_QUESTIONS = None
    automatic = None
    unigramNum = None
    bigramFreq = None
    trigramFreq = None
    quadgramFreq = None

    if automaticForm.submit1.data:
        formSubmit = True
        categories = [
            'Literature' if automaticForm.literature.data else '',
            'Science' if automaticForm.science.data else '',
            'Fine Arts' if automaticForm.fineArts.data else '',
            'History' if automaticForm.history.data else '',
            'Current Events' if automaticForm.currentEvents.data else '',
            'Geography' if automaticForm.geography.data else '',
            'Religion' if automaticForm.religion.data else '',
            'Mythology' if automaticForm.mythology.data else '',
            'Philosophy' if automaticForm.philosophy.data else '',
            'Social Science' if automaticForm.socialScience.data else '',
            'Other Academic' if automaticForm.otherAcademic.data else '',
            'Trash' if automaticForm.trash.data else ''
        ]
        categories = [i for i in categories if i]
        subcategories = [
            "American Literature" if automaticForm.americanLit.data else '',
            "British Literature" if automaticForm.britishLit.data else '',
            "Classical Literature" if automaticForm.classicalLit.data else '',
            "European Literature" if automaticForm.europeanLit.data else '',
            "World Literature" if automaticForm.worldLit.data else '',
            "Other Literature" if automaticForm.otherLit.data else '',
            "American History" if automaticForm.americanHis.data else '',
            "Ancient History" if automaticForm.ancientHis.data else '',
            "European History" if automaticForm.europeanHis.data else '',
            "World History" if automaticForm.worldHis.data else '',
            "Other History" if automaticForm.otherHis.data else '',
            "Biology" if automaticForm.biology.data else '',
            "Chemistry" if automaticForm.chemistry.data else '',
            "Physics" if automaticForm.physics.data else '',
            "Math" if automaticForm.math.data else '',
            "Other Science" if automaticForm.otherSci.data else '',
            "Visual Fine Arts" if automaticForm.visualFA.data else '',
            "Auditory Fine Arts" if automaticForm.auditoryFA.data else '',
            "Other Fine Arts" if automaticForm.otherFA.data else '',
            "Religion" if automaticForm.religion.data else '',
            "Mythology" if automaticForm.mythology.data else '',
            "Philosophy" if automaticForm.philosophy.data else '',
            "Social Science" if automaticForm.socialScience.data else '',
            "Current Events" if automaticForm.currentEvents.data else '',
            "Geography" if automaticForm.geography.data else '',
            "Other Academic" if automaticForm.otherAcademic.data else '',
            "Trash" if automaticForm.trash.data else ''
        ]
        payload = {
            "categories": categories,
            "subcategories": subcategories,
            "difficulties": [],
            "maxQueryReturnLength": "1000",
            "queryString": automaticForm.query.data,
            "questionType": "tossup",
            "randomize": False,
            "regex": False,
            "searchType": "answer",
            "setName": ""
        }

        resp = requests.post('https://www.qbreader.org/api/query',
                             json=payload)
        texts = [
            i['question'] for i in resp.json()['tossups']['questionArray']
        ]

        MAX_RESULTS = automaticForm.analyzeDetails.maxResults.data
        NUM_QUESTIONS = len(texts)
        automatic = automaticForm.analyzeDetails.automatic.data
        unigramNum = automaticForm.analyzeDetails.unigramNum.data
        bigramFreq = automaticForm.analyzeDetails.bigramFreq.data
        trigramFreq = automaticForm.analyzeDetails.trigramFreq.data
        quadgramFreq = automaticForm.analyzeDetails.quadgramFreq.data

    elif manualForm.submit2.data:
        formSubmit = True
        showAutomatic = False
        manualForm.jsonFile.data.seek(0)
        data = json.loads(manualForm.jsonFile.data.read())
        texts = [
            data["data"]["tossups"][i]["text"]
            for i in range(len(data["data"]["tossups"]))
        ]

        MAX_RESULTS = manualForm.analyzeDetails.maxResults.data
        NUM_QUESTIONS = len(texts)
        automatic = manualForm.analyzeDetails.automatic.data
        unigramNum = manualForm.analyzeDetails.unigramNum.data
        bigramFreq = manualForm.analyzeDetails.bigramFreq.data
        trigramFreq = manualForm.analyzeDetails.trigramFreq.data
        quadgramFreq = manualForm.analyzeDetails.quadgramFreq.data

    if formSubmit:
        if NUM_QUESTIONS:
            # Replace separators and punctuation with spaces
            text = re.sub(r'[.!?,:;/\-\s]', ' ', ' '.join(texts))
            # Remove extraneous chars
            text = re.sub(r'[\\|@#“”*$&~%\(\)*\"]', '', text)
            text = text.lower()

            toktok = ToktokTokenizer()
            STOPWORDS = [
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                'you', "you're", "you've", "you'll", "you'd", 'your', 'yours',
                'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
                "she's", 'her', 'hers', 'herself', 'it', "it's", 'its',
                'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
                'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
                'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
                'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
                'with', 'about', 'against', 'between', 'into', 'through',
                'during', 'before', 'after', 'above', 'below', 'to', 'from',
                'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
                'again', 'further', 'then', 'once', 'here', 'there', 'when',
                'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
                'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
                'can', 'will', 'just', 'don', "don't", 'should', "should've",
                'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren',
                "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn',
                "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
                "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',
                "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn',
                "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won',
                "won't", 'wouldn', "wouldn't"
            ]
            quizbowlKeywords = [
                'title', 'character', 'points', 'work', 'novel', 'poem',
                'book', 'name', 'story', 'man', 'one', 'narrator', 'novella',
                'author', 'another', 'found', 'comes', 'come', 'called',
                'poet', 'speaker', 'like', 'opens', 'includes', 'piece',
                'begins', 'use', 'used', 'features', 'played', 'within',
                'written', 'composer', 'protagonist', 'also', 'writer',
                'argues', 'argued', 'brought', 'claims', 'discussed', 'part',
                'ftp'
            ]

            allWords = toktok.tokenize(text)

            def common_unigrams(text, num=15, otherWords=[]):
                #Remove stopwords or quizbowl indicators
                stopwords = STOPWORDS + quizbowlKeywords + otherWords
                allWordExceptStopDist = nltk.FreqDist(
                    w for w in allWords
                    if len(w) > 2 and w.lower() not in stopwords
                    and not any([(w in i) for i in otherWords]))
                return [i[0] for i in allWordExceptStopDist.most_common(num)]

            def common_bigrams(text, frequency=0.40, otherWords=[]):
                bigram_measures = nltk.collocations.BigramAssocMeasures()

                # change this to read in your data
                finder = BigramCollocationFinder.from_words(allWords)

                # only bigrams that apper at certain frequency
                finder.apply_freq_filter(round(len(texts) * frequency))

                ignored_words = STOPWORDS + quizbowlKeywords
                finder.apply_word_filter(lambda w: len(w) < 3 or w.lower(
                ) in ignored_words or any([(w in i) for i in otherWords]))

                # return the 20 n-grams with the highest PMI
                results = finder.nbest(bigram_measures.pmi, 50)
                return [' '.join(i) for i in results]

            def common_trigrams(text, frequency=0.40, otherWords=[]):
                trigram_measures = nltk.collocations.TrigramAssocMeasures()

                # change this to read in your data
                finder = TrigramCollocationFinder.from_words(allWords)

                # only bigrams that apper at certain frequency
                finder.apply_freq_filter(round(len(texts) * frequency))

                ignored_words = STOPWORDS + quizbowlKeywords
                finder.apply_word_filter(lambda w: len(w) < 3 or w.lower(
                ) in ignored_words or any([(w in i) for i in otherWords]))

                # return the 20 n-grams with the highest PMI
                results = finder.nbest(trigram_measures.pmi, 50)
                return [' '.join(i) for i in results]

            def common_quadgrams(text, frequency=0.40, otherWords=[]):
                quadgram_measures = nltk.collocations.QuadgramAssocMeasures()

                # change this to read in your data
                finder = QuadgramCollocationFinder.from_words(allWords)

                # only bigrams that apper at certain frequency
                finder.apply_freq_filter(round(len(texts) * frequency))

                ignored_words = STOPWORDS + quizbowlKeywords
                finder.apply_word_filter(
                    lambda w: len(w) < 3 or w.lower() in ignored_words)

                # return the 20 n-grams with the highest PMI
                results = finder.nbest(quadgram_measures.pmi, 50)
                return [' '.join(i) for i in results]

            def automatic_solving(func,
                                  text,
                                  automatic,
                                  frequency=None,
                                  otherWords=[]):
                if automatic:
                    startingFrequency = 2 / NUM_QUESTIONS
                    results = func(text,
                                   frequency=startingFrequency,
                                   otherWords=otherWords)
                    while len(results) > MAX_RESULTS:
                        results = func(text,
                                       frequency=startingFrequency,
                                       otherWords=otherWords)
                        startingFrequency += 0.02
                    print(startingFrequency)
                    return results
                else:
                    return func(text,
                                frequency=frequency,
                                otherWords=otherWords)

            quadgrams = automatic_solving(common_quadgrams,
                                          text,
                                          automatic,
                                          frequency=quadgramFreq)
            trigrams = automatic_solving(common_trigrams,
                                         text,
                                         automatic,
                                         otherWords=quadgrams,
                                         frequency=trigramFreq)
            bigrams = automatic_solving(common_bigrams,
                                        text,
                                        automatic,
                                        otherWords=quadgrams + trigrams,
                                        frequency=bigramFreq)
            unigrams = common_unigrams(
                text,
                num=(MAX_RESULTS if automatic else unigramNum),
                otherWords=quadgrams + trigrams + bigrams)
            # print(unigrams)
            # print(bigrams)
            # print(trigrams)
            # print(quadgrams)

            data = [unigrams, bigrams, trigrams, quadgrams]
            stringData = ['\n'.join(i) for i in data]
            data.append(stringData)
        else:
            noResults = True
            data = []

    return render_template('analyze.html',
                           manualForm=manualForm,
                           automaticForm=automaticForm,
                           data=data,
                           showAutomatic=showAutomatic,
                           noResults=noResults)


app.run(host='0.0.0.0', port=81, debug=True)
