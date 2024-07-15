# TimeWise
Comprehensive task and time management tool

## Features
- Create and manage tasks
- Organize tasks into categories
- Assign tags to tasks
- Set due dates, priorities, statuses, time estimates, time spent, start dates, reminders, intervals, and custom fields for tasks
- Sort and filter tasks by various criteria
- Search for tasks
- Create custom views to display tasks in different ways
- RESTful API for programmatic access to tasks and categories
- Webhooks for real-time notifications
- Task templates
- Flexible recurring tasks

## Vision
TimeWise is a comprehensive task and time management tool that helps you stay organized and productive. With TimeWise, you can create and manage tasks, organize them into categories, and assign tags to them. You can set due dates, priorities, statuses, time estimates, time spent, start dates, reminders, intervals, and custom fields for tasks. You can sort and filter tasks by various criteria, search for tasks, and create custom views to display tasks in different ways. TimeWise is designed to be flexible and customizable, so you can use it in a way that works best for you.

TimeWize uses established standards and protocols to ensure interoperability with other tools and services. It provides a RESTful API for programmatic access to tasks and categories, and supports webhooks for real-time notifications. It is designed to be easy to use, with an intuitive user interface that is accessible on any device.

TimeWise is built on open-source technologies and is designed to be extensible and customizable. It is however not yet built with any security other than using HTTPS. Any required security features will be added in the future.

## Fields
### Title [Required, Unique, String, 1-255]
The title is the name of the task. It can be set for any task.

### Description [String, 0-4000]
The description is a detailed description of the task. It can be set for any task.

### Category [String, 0-255]
A category is a group of tasks. It can be a project, a class, a hobby, or anything else that you want to keep track of. Categories can be nested within other categories.

### Tags [List of Strings, 0-255]
Tags are labels that you can assign to tasks. They can be used to group tasks together, filter tasks, or search for tasks.

### Due Date [Date]
A due date is the date by which a task should be completed. It can be set for any task.

### Priority [Integer, 1-5]
A priority is a level of importance that you can assign to a task. It can be set for any task.

### Status [String, 0-255]
A status is the current state of a task. It can be set to "Not Started", "In Progress", "Completed", or "Deferred".

### Time Estimate (1y1M1d1h1m1s) [Time]
A time estimate is the amount of time that you think a task will take to complete. It can be set for any task that does not have subtasks. The time estimate for a task is the sum of the time estimates for all of its subtasks.

### Time Spent (1y1M1d1h1m1s) [Time]
Time spent is the amount of time that you have spent working on a task. It can be tracked for any task.

### Start Date [Date]
A start date is the date on which you plan to start working on a task. It can be set for any task.

### Reminders [List]
Reminders are notifications that you can set to remind you about a task they are set using webhooks.

### Interval [List]
An interval is a recurring time period that you can set for a task. It can be set for any task. Interval is set using the cron format. More than one interval can be set for a task.

### Recur from [String]
Recur from what event the interval should start. It can be set to due date or start date.

### Custom Fields
Custom fields are additional fields that you can add to tasks to store extra information. They can be used to store any type of data, such as text, numbers, dates, or URLs.

## Sorting
### Standard sort
Tasks can be sorted by due date, priority, status, time estimate, time spent, start date, or any custom field.

### Formulae sort
Tasks can be sorted using a formula that combines multiple fields. For example, you could sort tasks by priority and due date, or by time estimate and time spent. A standard formulae is provided and a formulae editor is available for custom formulae.

## Filtering
Tasks can be filtered by category, tag, due date, priority, status, time estimate, time spent, start date, or any custom field.

## Searching
Tasks can be searched by title, description, category, tag, due date, priority, status, time estimate, time spent, start date, or any custom field.

## Views
Create custom views to display tasks in different ways. Views can be saved and shared with other users.
