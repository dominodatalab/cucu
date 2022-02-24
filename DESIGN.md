# cucu design

This document will outline the design decisions made while building the `cucu`
framework and how everything works together to provide a reliable and useful
end to end testing framework.

# overview

`cucu` is an end to end testing framework that uses [gherkin](https://cucumber.io/docs/gherkin/)
to drive various underlying tools/frameworks to create real world testing
scenarios. As of now `cucu` uses selenium to interact with a browser but we 
will have support for running the tests through other selenium testing
frameworks.

There are a few reasons for writing the actual tests in `gherkin` including:

 * tests are readable by anyone in the organization, since they're just plain
   English that describe interactions and validations.
 * steps within a `gherkin` test can do actions on the browser, hit an API or
   anything else you can do programatically to simulate various other testing
   needs (ie use *iptables* to limit bandwidth, use *docker/kubectl* to
   pause/stop/restart containers, etc.)
 * there's only one implementation per "step" and this makes for better reusing
   of existing test code which can be maintained in the long term.

# cucu fuzzy matching

`cucu` uses selenium to interact with the browser but on top of that we've
developed a fuzzy matching set of rules that allow the framework to find
elements on the page by having a label and a type of element we're searching for.

The principal is simple you want to `click the button "Foo"` so we know you want
to find a button which can be one of a few different kind of HTML elements:

  * `<a>`
  * `<button>`
  * `<input type="button">`
  * `<* role="button">`
  * etc

We also know that it has the name you provided labeling it and that can be
done using any of the following rules:

  * `<thing>name</thing>`
  * `<*>name</*><thing></thing>`
  * `<thing attribute="name"></thing>`
  * `<*>name</*>...<thing>...`

Where `thing` is any of the previously identified element types. With the above
rules we created a simple method method that uses the those rules to find a set
of elements labeled with the name you provide and type of elements you're
looking for. We currently use [swizzle](https://github.com/jquery/sizzle) as
the underlying element query language as its highly portable and has a bit
useful features than basic CSS gives us.
