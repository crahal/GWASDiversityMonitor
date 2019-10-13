# Changelog

#### 22nd August 2019. Version 0.1.0.:
* Registered domain.
* Set up Heroku Dyno on free tier for prototyping.
* Pushed everything from local host onto GitHub.
* Launched prototype as deployed via Heroku CLI!

#### 25th August 2019. Version 0.2.0.:
* Added function to generate_data.py to create a zip of plotted csv sources.
* Changed Heroku settings to pull automatic updates from the GitHub repo.
* Upgraded the Dyno Type.
* Fixed some typing errors in the html files.
* Added new .html to serve the download link (linked to file in GitHub repo).
* Rewrote updating .sh to push changes to GitHub rather than Heroku master.
* Added changelogs

#### 26th August 2019. Version 0.2.1:
* Changed colormap of the doughnut chart upon user consultation.
* Added EFO traits to the hovertool of the bubble plot.

#### 27th August 2019. Version 0.3.0:
* New function tabulates most frequently analysed Parent terms.
* Added summary statistics to Tab related to most frequent terms of ancestry.

#### 28th August, 2019. Version 0.3.1:
* Fixed spacing issues
* Future proofed some of the back-end
* Enabled Automated Certificate Management (ACM) to manage TLS certificates.

#### 4th September, 2019. Version 0.4.0:
* Added ERC logo to represent their grateful contribution
* Added links to curators academic homepages.
* Replaced all strings away from basic 'Parents' to more clearly relate to 'Parent Categories'
* Replaced all references to 'dohnut' with references to 'doughnut'
* Added brief descriptions of all widgets and relevant hyperlinks
* Renamed 'About' tab to 'Additional Information'
* Added 'Figure X' into the titles of the 'Interactive Figures' tab.
* Set up proper caching of all of the old files served up by the Catalog

#### 6th September, 2019. Version 0.4.1:
* Stopped titles running over on fixed scaling.
* Added direct to 'Additional Information' tab.
* Fixed typo on summary_stats.html.

#### 7th September, 2019. Version 0.4.2:
* Changed name of parent widget to 'Parent Category'
* Changed Parent Category widget to default to 'Cancer'
* Changed version number in the downloaddata.html
* Added a dedicated License file

#### 8th September, 2019. Version 0.5.0:
* Added percentage stats to the Interactive Figures tab (and their dynamic updating)
* Moved links to above the widgets
* Added a link to privacy policy
* Renamed 'Initial Stage' to 'Discovery Stage'
* Shortened 'Figure' to 'Fig' to stop some titles getting cut off
* Moved legend position on Fig 2
* Changed color on Fig 1 European and Asian reversed
* Better layout alignment.

#### 10th September, 2019. Version 0.5.1:
* A few layout and title tweaks

#### 12th September, 2019. Version 0.6.0:
* Major rehaul -- dashboard is now roots embedded into a jinja template
* Moved all htmls into the jinja template
* A lot of reworkings to the html
* New header
* Added slider application to the bubble plot
* Moved slider to the widget set and added title to it

#### 12th September, 2019. Version 0.7.0:
* Reworked the summary part with cards and pill badges
* removed colourbar and moved the slider

#### 19th September, 2019. Version 0.7.1:
* Increased the number of plots effected by the Year slider
* Fixed an axis formatting bug of the time series plot
* Better spacing in the summary part.
* Fixed a bug with the html title
* Small minor typing corrections

#### 13th October, 2019. Version 0.8.0:
* Moved figure 5 to bottom left for better sizing, and moved the major tick labels inside the axis.
* Added an additional time series plot (Fig 2 split into Fig2a and Fig2b).
* Better sized the doughnut chart, and dropped the 'in part not recorded' rows from it.
* Added 'All' parent and ancestry terms back into the widgets.
* Set the tick formatter on the bubble chart to make it consistent across ancestries (and the corresponding sizes) for alignment.
* Added additional acknowledgements to both the github and the dashboard
* Some light code refactoring and docstring work.
