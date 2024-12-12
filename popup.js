console.clear

/** search the current website for specific words */
// based on https://stackoverflow.com/questions/74409759/chrome-extension-that-searches-for-text-in-a-page-then-changes-the-message-on-th
const searchWord = () => {
    //checking to see where printing occurs, for "inspect" on extension HTML or webpage HTML
    console.log("comment inside searchWord function :)") /* doesn't print */

    const text = document.body.textContent ; 
    const flower = text.includes("flower" || "Flower") ;

    /* get all the text data on the page */
    const allInnerText = document.body.innerText ;

    return{
      oneWord: flower,
      otherData: allInnerText,
      otherData2: 4
    }
}

// no longer using this, but this was finding just one word on the page
// showing result of search wrokd
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
        target: { tabId: tabs[0].id},
        func: searchWord
    }, (result) => {
                     
        if (result[0].result.oneWord){
          // indicating if this current tab has or does not have "flower" info
            console.log("found some flowers!")
            const pageResult = " ";
            document.getElementById("foundWord").innerText = pageResult; 

        } else {
            console.log("didn't find flowers")
        }
    }
)

}


)

/**Heroku app python 
 * Go button will send data to python in flask
 * Originally included URL to be able to add new videos
*/

document.addEventListener('DOMContentLoaded', function() {
    //const button = document.getElementById('process-button'); // hello world button
    const sendInputButton = document.getElementById('send-input-button');
    const resultElement = document.getElementById('result');

    /*
    // this is the button to add new video
    button.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            fetchHelloWorld()
                .then(result => {
                    resultElement.textContent = result;
                })
                .catch(error => {
                    resultElement.textContent = "Error: " + error;
                });
        }); // end of chrome.tabs.query
    });
    */
    // this is button tat retuns top 3 video results
    // if clicked, send current url and all content
    sendInputButton.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {

            /*
            chrome.tabs.sendMessage(tabs[0].id, {action: "getPageData"}, (response)=> {
                if (chrome.runtime.lastError){
                    resultElement.textContent = "error page results";
                    return ;
                }
            */
                // in jecting script https://developer.chrome.com/docs/extensions/reference/api/scripting
                chrome.scripting.executeScript( ///)
                    {
                        // to the current tab
                        target: {tabId: tabs[0].id},
                        func: ()=>{
                            return {
                                // getting current url and full text
                                url: window.location.href,
                                content: document.body.innerText || '',
                            };
                        },
                    },
                    (injectedResults)=>{  //} closing bracket after sned data to flask
                        if (chrome.runtime.lastError){
                            console.error(chrome.runtime.lastError.message);
                            resultElement.textContent = 'page data error' ;
                            return ; 
                        }

                    // retreiving data from injection resutls
                    const pageData = injectedResults[0].result ; 
                    const{url, content} = pageData ; 

                    //const url = pageData[0];
                    //const content = pageData[1];

                    // website URL, text content  -- this doesn't work, gives popup html instead, have to use script injection
                    const currentUrl = window.location.href;
                    const pageContent = document.body.textContent;

                    // showing actual URL and content
                    console.log('current URL', url) ;
                    console.log('pageContent', content.substring(0,200) ) ;

                    //const {url, content} = response ; 
                            
                    // Send the data to the Flask app
                    sendDataToFlask( url, content) //url, content )//currentUrl, pageContent)
                    .then(python_response => {
                        if (python_response.result) {
                            const{ url, is_youtube, word_output, n1_video_id, n1_video_title, n2_video_id, n2_video_title, n3_video_id, n3_video_title } = python_response.result ; 
                            resultElement.textContent = `Found top 3 videos`;
                            //resultElement.textContent = `Output URL: ${url}\n HasYoutube: ${is_youtube}\n Links: ${word_output}`;
                            
                            // first Link disply a link
                            const YT_url = "https://www.youtube.com/watch?v="+`${n1_video_id}` ;
                            //const YT_linkDesc = "https://www.youtube.com/watch?v="+`${n1_video_id}` ;
                            const YT_linkDesc = `${n1_video_title}`; //"Video:;

                            // https://www.geeksforgeeks.org/how-to-create-a-link-in-javascript/
                            const link = document.createElement('a')
                            link.href = YT_url ;
                            link.textContent = YT_linkDesc ;
                            link.target = "_blank" // to open in new tab when clicked
                            
                            const contatiner = document.getElementById('youtube-link');
                            contatiner.appendChild(link) ;
                            
                            // 2nd Link disply a link
                            const YT_url_2 = "https://www.youtube.com/watch?v="+`${n2_video_id}` ;
                            const YT_linkDesc_2 = `${n2_video_title}` ;
                            //const YT_linkDesc = `Output URL: ${n1_video_title}`; //"Video: https://www.youtube.com/watch?v=I2dHYSbH0a4" ;

                            const link_2 = document.createElement('a')
                            link_2.href = YT_url_2 ;
                            link_2.textContent = YT_linkDesc_2 ;
                            link_2.target = "_blank" // to open in new tab when clicked
                            
                            const contatiner_2 = document.getElementById('youtube-link2');
                            contatiner_2.appendChild(link_2) ;

                            // 3rd Link disply a link
                            const YT_url_3 = "https://www.youtube.com/watch?v="+`${n3_video_id}` ;
                            const YT_linkDesc_3 = `${n3_video_title}` ;
                            //const YT_linkDesc = `Output URL: ${n1_video_title}`; //"Video: https://www.youtube.com/watch?v=I2dHYSbH0a4" ;

                            const link_3 = document.createElement('a')
                            link_3.href = YT_url_3 ;
                            link_3.textContent = YT_linkDesc_3 ;
                            link_3.target = "_blank" // to open in new tab when clicked
                            
                            const contatiner_3 = document.getElementById('youtube-link3');
                            contatiner_3.appendChild(link_3) ;

                        } else {
                            resultElement.textContent = "error: missing " ;
                        }

                        //resultElement.textContent = `Output: ${response.result}`;
                    })
                    .catch(error => {
                        resultElement.textContent = "Error: " + error;
                    });
                });// end of execute script
            });
        });  
    //});

    });

//});

// only using this to test Heroku early on
function fetchHelloWorld() {
    return fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/hello')  
        .then(response => response.text())
        .then(data => {
            return data;
        });
}

// when button clicked, send to app

// sends data to flask and waits for response
// asynchronous because it has to wait for results
async function sendDataToFlask(url, content) {
    try {
        // POST method receiveds data from the extension
        const response = await fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/send-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // url and full text contents of current tab
            body: JSON.stringify({url: url, content: content}),
        });

        // for error hankling
        if(!response.ok){
            throw new Error(`error : ${response.status}`) ;
        }
        // wait for the response to come from python, don't just end right away, hence asynchronocus func
        const flaskdata = await response.json();
        return flaskdata ;
    } catch (error){
        console.error("error in sending/receiving Flask data", error);
        throw error ; 

    }
}
