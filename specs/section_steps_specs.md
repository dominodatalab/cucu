# Section Steps Implementation Specification

## Overview

This specification outlines the enhancement of the existing comment step functionality in cucu to support hierarchical section steps. This improvement will provide better organization and visual structure to test scenarios, making them more readable and maintainable.

## Current Implementation

The current implementation has a simple comment step feature:

- Located in `src/cucu/steps/comment_steps.py`
- Provides a single level of heading using the `#` symbol
- Functions as a no-op step that only serves as visual marker in reports
- Has limited formatting capabilities in the HTML report

## Requirements

The enhanced section steps functionality needs to:

1. Support hierarchical heading levels similar to Markdown (# for h1, ## for h2, etc.)
2. Provide appropriate visual styling in HTML reports based on heading level
3. Create a logical structure for grouping steps within scenarios
4. Support up to 4 levels of nesting
5. Maintain backward compatibility with existing tests using the `#` comment style
6. Properly integrate with the database schema (when database functionality is enabled)

## Implementation Changes

1. **File Renaming**:
   - Rename `src/cucu/steps/comment_steps.py` to `src/cucu/steps/section_steps.py`
   - Update all imports and references accordingly

2. **Step Definition Changes**:
   - Update the step pattern to recognize multiple heading levels
   - Parse the number of `#` characters to determine heading level
   - Keep backward compatibility with existing single `#` usage

3. **HTML Report Formatting**:
   - Add CSS styles for different heading levels
   - Format heading levels with appropriate HTML tags
   - Use proper indentation in the HTML report

4. **Step Execution**:
   - Keep the step implementation as a no-op
   - Record section metadata for reporting and database tracking

## Section Level Handling

The implementation will support the following heading levels:

| Syntax | Heading Level | HTML Equivalent | Visual Style |
|--------|--------------|-----------------|--------------|
| # | 1 | h1 | Large, bold, with bottom border |
| ## | 2 | h2 | Medium, bold |
| ### | 3 | h3 | Small, bold |
| #### | 4 | h4 | Small, italic |

Section nesting will follow standard markdown rules:

- A subsection belongs to the nearest preceding section of a higher level
- Sibling sections at the same level create parallel groupings
- Steps following a section belong to that section until another section is encountered

## Example Usage

```gherkin
Feature: Sample feature showing section headings

  Scenario: Using section headings for organization
    * # Main Section
    * This step belongs to the main section
    * So does this one
    
    * ## Subsection A
    * This step belongs to Subsection A
    * And so does this one
    
    * ## Subsection B
    * This step is in Subsection B
    
    * ### Deeper subsection
    * A step in the deeper section
    * Another step in the deeper section
    
    * ## Back to level 2
    * This step is in a new level 2 section
```

## HTML Report Rendering

The HTML report should format section headings with:

1. Proper indentation reflecting the nesting level
2. Appropriate font size and weight
3. Visual separation from regular steps
4. Consistent styling throughout the report

## Implementation Plan

1. Create the new `section_steps.py` file with enhanced functionality
2. Update HTML templates to support different heading levels
3. Update any test cases that rely on the current comment step behavior
4. Add test cases for the new heading level functionality
5. Update documentation to reflect the new capabilities

## Backward Compatibility

The implementation will maintain backward compatibility by:

- Supporting the current single `#` syntax with the same behavior
- Not changing how existing comment steps are rendered in reports
- Ensuring existing tests continue to pass with the new implementation

This specification serves as a prerequisite for the database implementation, as the section structure is a key component of the database schema design.
