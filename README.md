# Headpage (WIP)

A Simple and porpousely vulnerable django web-application for testing and learning

## Idea

* Create a social-media-like (Headpage != Facebook) web application with a relatively small, and vulnerable, code base. 
* Users create public profiles, upload files for public (such as photos)or private (such as pdfs) use and browse other users' profiles.

## Main Vulnerabilities

### Illegal File Access
* Profile pictures are stored as static files in the site with standardized name `user_(user_id)avatar`. They appear in the User's profile as a thumbnail. "Full Resolution" pictures are accessible by using their filename, e.g. `headpage.example/social/static?file=user1_avatar.jpg` The `file` in the GET is not properly validated/sanitized

### SQL Injection
* User pages are accessible using paramters "headpage.example/user?id=1". The parameter is used in a raw SQL SELECT, to load the user's data for the page
* Login screen also pass login and password as GET parameters that are not sanitized

### Remote Code Execution
* (based on the django.nV injection vuln) The user can upload a file and give an arbitrary name (or rename already uploaded files). When first uploaded the files are stored in a temporary folder, before being moved to a `userfiles` folder by invoking `mv` from the `os`. The rename is also done with `mv`. This process is vulnerable to code injection in the new file name, or replacing an existing program with a malicious version, such as `/bin/ls`
* The user can choose a picture already uploaded for his profile picture, or download an image from a URL. The download done by invoking `wget` without escaping the user input or validating the filetype. 

### Open Redirect
* When clicking the link to the login page from a previous page, the previous Page URL is sent as a Parameter for a redirection back to the previous page after loging in. The redirection URL is not validated. E.g. in the index, the link goes to headpage.example/login?redirect=headpage.example/index 
`if(valid(request.getParameter("usr"),request.getParameter("pwd"))) response.sendRedirect(request.getParameter("redirect"));`


### Malicious File Upload
* Upload malware as pictures, the site does not validate filetype
## Database Models

### User
Self-explanatory
* `username`
* `password` (SHA-1 , unsalted)
* `files`
* `name`
* `about`

### Files
User submited files (Shamelessly copying this idea from django.nV)
* `name`
* `path`
* `is_public`

## Views
### Index
Listing all Users (Maybe afterwards paging and a (vulnerable) search bar)
### User profile
The static page where the user information is shown
### Login screen 
### Edit profile