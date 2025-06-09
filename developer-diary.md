# GameStudy Developer Diary

---
This developer diary records the planning, design, development, and testing phases of the GameStudy application. Entries are made regularly to track progress, challenges, and decisions throughout the software development lifecycle.

## Developer Diary Entry #1

**Title:** Final Project Idea  
**Date:** 14/04/25

Today I finalized my idea for the project, a study app called GameStudy. The concept is to create a game-like experience where users progress in a simple game by logging study hours. The goal is to motivate students to study more by turning studying into something fun, competitive, and rewarding.

This project was inspired by the growing issue of students struggling with distractions, lack of motivation, and short attention spans, often due to social media. GameStudy aims to flip that by giving students a reason to stay focused and productive, using game mechanics to replace unproductive screen time. The app will be built as a progressive web app (PWA) so it works on both desktop and mobile. The focus will be the study timer and game integration, keeping things lightweight and engaging.

---

## Developer Diary Entry #2

**Title:** SRS Creation and Progression  
**Date:** 16/04/25

Today I completed the first draft of the SRS for GameStudy. I outlined the app’s purpose, its core features (like the study timer, XP system, and achievements), and defined the main user base, being the students needing motivation to study. I simplified the non-functional requirements to keep them broad, while ensuring security was clearly covered, including bcrypt hashing and input sanitization. I chose not to include a separate “User Needs” section, as it’s already covered through other parts of the document. Overall, the SRS now provides a clear outline for development moving forward.

---

## Developer Diary Entry #3

**Title:** Implementation Method Chosen and Financial Feasibility Study created  
**Date:** 19/04/25

Today I worked on finalizing and justifying the implementation method for the GameStudy project. Out of the 4 available implementation methods, phased implementation was chosen as the best fit for the app's needs. This method will allow us to roll out features in sprints, starting with core functionality like the study timer and user profiles, and more complex elements like player leaderboards and other features later. The phased approach minimizes risk and will also allow for continuous feedback during development. I have also begun working on the Financial Feasibility Study. This included outlining as specifically as possible the planned application, target markets, and unique characteristics of the application, as well as preparing a projected costs statement.

---

## Developer Diary Entry #4

**Title:** Financial Feasibility Study completed  
**Date:** 21/04/25

Today I completed the financial feasibility report on the GameStudy project. This included filling out the projected costs statement, estimating first-year development and operating costs, and outlining projected revenue based on market research. I defined the value proposition of the application as motivating students to stay engaged by monitoring study using gamification and identified a clearly established gap / niche in the market for this type of product. I had also analyzed competitor's services, assessed their pros and cons, and strategically placed GameStudy. An Opening Day Balance Sheet was created that listed all assets required and potential liabilities. Finally, I checked all the information to ensure the projections are realistic and within the project's scope. From this, the project was determined to be financially viable, and the analysis justifies the decision.

---

## Developer Diary Entry #5

**Title:** SWOT Analysis, Storyboard Created and Completed, Pitch Design  
**Date:** 23/04/25

Project Pitch

Today I completed the SWOT analysis for the phased implementation method chosen for GameStudy. I broke down the internal strengths and weaknesses, as well as the external opportunities and threats, and organized them into detailed paragraph form. This analysis will help communicate why phased implementation is the most suitable strategy for the app and what factors we should be prepared for as development progresses. I also began developing visual content for the project pitch, particularly focusing on the storyboard. I created a four-panel storyboard that outlines the basic user interface in GameStudy, from logging in to tracking study time and earning achievements. The storyboard gives a simple preview of what the user interface will look like. I then worked on structuring the project's pitch. I began organizing the content, including the SRSD key points, implementation justification, financial feasibility summary, and now the SWOT analysis and storyboard into a clear and professional format.

---

## Developer Diary Entry #6

**Title:** Begun Research & Planning, Social and Ethical Issues  
**Date:** 27/04/25

Today I committed to establishing GameStudy's underlying social and ethical basis, starting with accessibility requirements like screen reader support and low-bandwidth capability to make it accessible to everyone of all socioeconomic classes, and sustainable development standards like power-saving programming and server hosting to reduce our impact on the planet. On the ethical side, I investigated other interaction models, giving up on addictive features like Duolingo streaks and instead committing to healthier Forest-style balanced usage reminders, and authored key privacy policies from Quizlet's open data principle, though this revealed we'll need additional development time for full accessibility integration and should plan more towards green hosting solutions. I also understood that we need cultural consultation in designing avatars and themes so that we do not engage in stereotypes and combining all these learnings into a brief that we are going to utilize tomorrow during our prototyping period and ensuring we address all these social and ethical issues ahead of time.

---

## Developer Diary Entry #7

**Title:** Compliance and Legislative Issues addressed  
**Date:** 1/05/25

I conducted research on legal and compliance issues that the GameStudy project needs to meet as well as how to mitigate them. The app, as it would be monitoring personal study routines and account information, must comply with the Australian Privacy Act (1988) and NSW Privacy and Personal Information Protection Act (1998), which respectively ensure that personal information are gathered, stored, and handled securely. I also considered copyright compliance, especially regarding any icons, sounds, or visual assets used in the app. To avoid infringement, I’ll ensure all media is either original, royalty-free, or licensed for use. This research will guide my decisions around data handling and content throughout development.

---

## Developer Diary Entry #8

**Title:** Created Diagrams of System  
**Date:** 5/05/25

Today I created Level 0 and Level 1 Data Flow Diagrams (DFD) for the GameStudy project. These diagrams provide an overview of how data moves through the system, including interactions between external users and internal processes. The Level 0 DFD describes the system's main inputs and outputs, whereas the Level 1 DFD digs deeper into internal functions like data handling, authentication, and study tracking.

---

## Developer Diary Entry #9

**Title:** Structure Chart and Data Dictionary  
**Date:** 8/05/25

Today I developed a Structure Chart and Data Dictionary for the GameStudy project. The Structure Chart shows how the system modules are arranged and interact with one another. This clarifies the flow of control and the breakdown of the operation. The Data Dictionary outlines the key data items utilized in the system, including their types, forms, and goals.

---

## Developer Diary Entry #10

**Title:** Gantt Chart and Class Diagrams  
**Date:** 13/05/25

Today I created a Gantt chart for my project which allows me to view and schedule my sprints in order to finish the task on time. I have also created UML class diagrams which show the different methods and properties of each class.

---

## Developer Diary Entry #11

**Title:** UAT Document  
**Date:** 16/05/25

Today I started writing the User Acceptance Testing (UAT) documentation for GameStudy.  This included creating test scenarios centred on important elements such as the study timer, achievements, and user authentication. This document's purpose is to guarantee that the software project meets the functional requirements of the client prior to the final release. 

---

## Developer Diary Entry #12

**Title:** Quality Assurance Criteria and Software Development Approach  
**Date:** 23/05/25

Today I completed quality assurance requirements for GameStudy, including metrics for usability, dependability, and security. I also documented the chosen software development approach, being the agile approach, confirming the phased sprints model which emphasises integration and testing through consistent feedback.

---

## Developer Diary Entry #13
**Title:** Sprint 1 Start and Finish
**Date:** 25/05/25

Today was the beginning and completion of Sprint 1. The focus was on setting up the project structure, initializing the repository, and implementing the basic user authentication system. I created the user registration and login pages, set up session management, and ensured password security using bcrypt. The database schema for users was finalized and tested. By the end of the sprint, users could sign up, log in, and log out successfully. This established the foundation for all future development.


---

## Developer Diary Entry #14
**Title:** Sprint 2 Start and Finish
**Date:** 29/05/25

Sprint 2 focused on building the core study timer functionality. I designed and implemented the timer UI, allowing users to start, pause, reset, and save their study sessions. The backend was updated to log study time for each user, and the timer state was made persistent using localStorage. I also added basic error handling and notifications for session events. Testing confirmed that study sessions were being tracked and saved correctly. This sprint delivered the main feature of the app and prepared the groundwork for gamification.

---

## Developer Diary Entry #15
**Title:** Sprint 3 Start and Finish
**Date:** 31/05/25

Sprint 3 was dedicated to the achievements system. I designed the achievements database schema and implemented backend logic to check eligibility and award achievements automatically based on study time and XP. The frontend was updated to display achievements with badges and progress bars, and a notification system was added for real-time achievement unlocks. I also improved the dashboard UI to showcase user progress. Testing ensured that achievements were awarded and displayed correctly. This sprint added a major motivational feature to the app.

---

## Developer Diary Entry #16
**Title:** Sprint 4 Start and Finish  
**Date:** 31/05/25

Sprint 4 was dedicated to enhance the gamification aspect, I added visual rank badges for the top 1, 2, 3, 5, 10, and 20 users, as well as fun achievement badges for all participants. The leaderboard UI was improved with a podium for the top three users, filter buttons for different time periods (all time, this week, today), and a personal highlight for the logged-in user. I also refined the progress bar logic on both the study timer and achievements pages to ensure accurate and responsive feedback.

---
## Developer Diary Entry #16
**Title:** Sprint 5 Start and Finish  
**Date:** 1/06/25

Sprint 5 focused on refining the user experience, gamification aspects and addressing feedback from previous sprints. The main improvements included replacing the Bootstrap progress bars with emoji-based progress bars for both the achievements and study timer pages, making progress more visually engaging and accessible. The motivational quote feature was updated to rotate every 5 minutes, providing ongoing encouragement during study sessions. Session goal options were standardized to 30, 60, and 90 minutes for consistency across the app. I also resolved Content Security Policy (CSP) issues by moving all inline JavaScript into external files, ensuring compatibility and improved security. Extensive testing confirmed that the emoji progress bar, motivational quotes, and session goal logic all functioned as intended. This sprint delivered a more polished and motivating interface, setting the stage for future enhancements.


---

## Developer Diary Entry #17
**Title:** Sprint 6 Start 
**Date:** 1/06/25


Sprint 6 has begun, with the main focus on UI polish and preparing for advanced features. My immediate goals are to modernize the app’s look and feel, improve accessibility, and lay the groundwork for new motivational features. This sprint, I plan to enhance the dashboard with more dynamic elements, update the color palette and branding, and ensure accessibility improvements like better keyboard navigation and contrast. I have not yet started work on advanced features such as daily challenges with XP rewards or progress tracking analytics, but these are planned for the upcoming days in this sprint. The next steps will involve designing the database structure and backend logic for daily challenges, so users can receive new challenges each day and earn XP for completing them. Overall, Sprint 6 is set up to deliver both visual improvements and the foundation for new features to keep users engaged.


---

## Developer Diary Entry #18
**Title:** Sprint 6 Advanced Features (Challenges)
**Date:** 3/06/25

Today I implemented the advanced daily challenges feature for GameStudy. I designed and created new challenge types such as "Study for 30 minutes" and "Complete 2 study sessions," and updated the backend logic to automatically track and complete these challenges based on user activity.Testing confirmed that challenges are assigned daily, tracked accurately, and update in real time as users study. 

---

## Developer Diary Entry #19
**Title:** Finished Sprint 6
**Date:** 4/06/25

Sprint 6 concluded with the successful integration of daily challenges and further UI improvements. I finalized the backend logic for assigning and tracking daily challenges, ensuring users receive new, randomized challenges each day. I also polished the leaderboard and achievements pages for a more cohesive look and improved accessibility.

---

## Developer Diary Entry #20
**Title:** Sprint 7 - Fixed Reset Password Feature and Code Cleanup  
**Date:** 7/06/25

Today I fixed the reset password feature, which previously had issues with token validation and password updates. I removed unnecessary or redundant code from both the backend and templates, resulting in a cleaner and more maintainable codebase. Minor UI tweaks were made to keep the app visually consistent. With these fixes, the password reset process is now reliable and the overall code quality has improved.

---

## Developer Diary Entry #20
**Title:** Sprint 7 - Analytics Page Development 
**Date:** 9/06/25

Today I finished developing the Analytics page for GameStudy. The goal is to provide users with real-time feedback on their study habits, including server status, session stats, and XP progress charts. I implemented interactive filtering for the XP charts, allowing users to view their study progress by day, week, or month. Both line and bar charts are now available, providing multiple visualizations of XP earned over time.The server status and user study stats now load dynamically and display in real time. Testing confirmed that all analytics features work as intended, with accurate filtering and responsive chart updates.
---

## Developer Diary Entry #21
**Title:** 
**Date:**


---