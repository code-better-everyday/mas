from mrjob.job import MRJob

class MRSalaries(MRJob):

    def mapper(self, _, line):
        try:
            (name,jobTitle,agencyID,agency,hireDate,annualSalary,grossPay) = line.split('\t')
            salary = float(annualSalary.replace(',', '').replace('$', ''))
        except ValueError:
            return

        if salary >= 100000:
            band = 'High'
        elif salary >= 50000:
            band = 'Medium'
        else:
            band = 'Low'

        yield band, 1

    def combiner(self, band, counts):
        yield band, sum(counts)

    def reducer(self, band, counts):
        yield band, sum(counts)


if __name__ == '__main__':
    MRSalaries.run()


