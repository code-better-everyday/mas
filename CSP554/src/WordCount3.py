from mrjob.job import MRJob
import re

WORD_RE = re.compile(r"[\w']+")


class MRWordCount(MRJob):

    def mapper(self, _, line):
        for word in WORD_RE.findall(line):
            yield len(word), 1

    def combiner(self, length, counts):
        yield length, sum(counts)

    def reducer(self, length, counts):
        yield length, sum(counts)


if __name__ == '__main__':
    MRWordCount.run()


