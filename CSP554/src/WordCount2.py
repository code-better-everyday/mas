from mrjob.job import MRJob
import re

WORD_RE = re.compile(r"[\w']+")


class MRWordCount(MRJob):

    def mapper(self, _, line):
        for word in WORD_RE.findall(line):
            first = word.lower()[0]
            if 'a' <= first <= 'n':
                yield 'a-n', 1
            else:
                yield 'other', 1

    def combiner(self, bucket, counts):
        yield bucket, sum(counts)

    def reducer(self, bucket, counts):
        yield bucket, sum(counts)


if __name__ == '__main__':
    MRWordCount.run()


