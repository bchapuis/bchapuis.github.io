---
layout: post
title: "Code Coverage for Maven Projects with Cobertura, CircleCI and Codecov"
date: 2019-02-05 17:30:00
author: <a href="/">Bertil Chapuis</a>
intro: >
    As Google remained relatively quiet on the topic of sending cobertura code coverage reports from CircleCI to Codecov, I decided to give it a try. Surprisingly, the integration was much easier than expected, thanks to an amazing bash script provided by Codecov!
---

[CircleCI](circleci.com), [Codecov](https://codecov.io/) and [Cobertura](http://cobertura.github.io/cobertura/) are very good tools that integrate well together. As of writing the only missing piece is the documentation.

In order to generate a Cobertura code coverage report for your Java project, you simply need to add the following plugin to your `pom.xml` file.

```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>cobertura-maven-plugin</artifactId>
    <version>2.7</version>
    <configuration>
        <formats>
            <format>html</format>
            <format>xml</format>
        </formats>
        <check/>
    </configuration>
</plugin>
```

Then, the maven goal `cobertura:cobertura` generates an xml and an html report for your project, both of which are located in the `target/site/cobertura` directory. The html format is pretty handful, however what about sending the xml report to Codecov?

CircleCI can easily be configured to perform this operation after each build. The following `.circleci/config.yml` file illustrates how this can be done.

```yaml
version: 2
jobs:
  build:
    docker:
      - image: circleci/openjdk:8u181-jdk
    working_directory: ~/repo
    environment:
      MAVEN_OPTS: -Xmx3200m
    steps:
      - checkout
      - restore_cache:
          keys:
            - v1-dependencies-{{ checksum "pom.xml" }}
            - v1-dependencies-
      - run: mvn install
      - run: mvn test
      - run: "mvn cobertura:cobertura"
      - run: "bash <(curl -s https://codecov.io/bash)"
      - save_cache:
          paths:
            - ~/.m2
          key: v1-dependencies-{{ checksum "pom.xml" }}
```

Codecov did quite an amazing job with their [bash script](https://codecov.io/bash) that supports an impressive list of reports and formats, among which Cobertura. That's it, tokens are not needed for public projects and a nice report will appear on your Codecov dashboard.



