# Instagram Crawler
_Last Updated: 30 Jul 2019_

This crawler focuses on collecting the following data:
- Image
  - Number of likes
  - Number of comments
  - Timestamp

## Usage
```
usage: inscrawler.py [-h] [-f FILEPATH] [-i INDEX] [-n NUM]

optional arguments:
  -h, --help            show this help message and exit
  -f FILEPATH, --filepath FILEPATH
                        Username filepath, default is ./users.csv
  -i INDEX, --index INDEX
                        Index of user you want to start with, default is 0
  -n NUM, --num NUM     Number of users to collect, default is 1
```

## Saving Images
### Image Name
Each image will be saved under the filename:
`num_of_likes-num_of_comments-timestamp.jpg`

### File Structure
The images will be saved into the following file structure:
```
instagram-crawler
└── Influencers
    └── influencer1_username
        ├── img1.jpg
        │   img2.jpg
        .
        .
        .
    └── influencer2_username
    .
    .
    .
```

## References
Mikhail Sisin: [How to scrape pages with infinite scroll: extracting data from Instagram](https://www.diggernaut.com/blog/how-to-scrape-pages-infinite-scroll-extracting-data-from-instagram/)
