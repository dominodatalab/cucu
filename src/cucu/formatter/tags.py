from behave.formatter.base import Formatter


class CucuTagCollectorFormatter(Formatter):
    name = "tags.filter"
    description = "list tags that match a certain regular expression"

    def __init__(self, stream_opener, config):
        super(CucuTagCollectorFormatter, self).__init__(stream_opener, config)
        self.tags = set()

    def uri(self, uri):
        pass

    def feature(self, feature):
        if feature.should_run(config=self.config):
            [self.tags.add(tag) for tag in feature.tags]

    def scenario(self, scenario):
        if scenario.should_run(config=self.config):
            [self.tags.add(tag) for tag in scenario.tags]

    def close(self):
        self.open()
        self.stream.write("\n".join(sorted(self.tags)) + "\n")
        self.close_stream()
