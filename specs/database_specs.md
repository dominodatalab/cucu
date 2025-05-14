# Cucu Run Database Requirements Spec

We want to have cucu create a database to store all relevant `cucu run` test data.
- Have a CLI arg to turn on this feature (off by default)
- Keep the existing output (png files, directory structures, json, logs, etc)
- Create a single `results/results.db` duckdb database file at the start (if it doesn't exist)
- The same db is shared between workers
- The db is updated in real time, before, during and after any action that generates data
- Workers need to make sure to have access and not cause race conditions or deadlocks
- The db should be a valid database even when the cucu process is killed or when a worker is killed
- Don't store png files in the database, but instead add the meta data of the files to the database
- Create tables that follow from running tests. See below for more 



## Tables
The table layout should be the following, with appropriate primary keys and foriegn keys linking them.
All tables entries have an ID column with the naming convention of `{tablename}_ID`.
1. CucuRun - there should be one master entry per `cucu run`, even with multiple workers. This should have all the data generated in the run_details.json, but shouldn't load it from the file.
2. Feature - maps to a feature file. Features don't actually run, but their Scenarios do. Include the feature description.
3. Scenario - maps to a scenario in a feature file. Include all the tags, with tags inheirited from the feature. Also scenario description.
4. Section - maps to a special step and provides grouping to steps that follow it (see section steps). Sections could have sub-sections. Each sub-section has a link back to the parent section. Add the section level.
5. Step - maps to the step (except section steps) in the scenario. Steps could have multiple sub-steps. Add the step level with link to parent.
6. StepRun - Steps can be retried so we need to support recording each retry as a separate row. These can also be associated with a screenshot
7. StepPost - ocurrs at the end of of a StepRun which takes a screenshot after the last StepRun


## Section Steps
This is a special step that helps divide a scenario into groups.
Currently it is called `comment_step` and has a `#` that is parallel to the markdown heading levels `#, ##, ##`
- Change this to be called `section_step` (including filename) and all its correspending tests.
- Implement different heading levels `#, ##, ###, ####` and change the html to show corresponding levels
For purposes of the database - these heading sections should group the steps that follow according to the same rules as markdown headings.

