from mrjob.job import MRJob
import re

WORD_RE = re.compile(r"[\w']+")


class MRWordCount(MRJob):

    def mapper(self, _, line):
        words = [word.lower() for word in WORD_RE.findall(line)]
        for i in range(len(words) - 1):
            yield f"{words[i]} {words[i + 1]}", 1

    def combiner(self, bigram, counts):
        yield bigram, sum(counts)

    def reducer(self, bigram, counts):
        yield bigram, sum(counts)


if __name__ == '__main__':
    MRWordCount.run()


