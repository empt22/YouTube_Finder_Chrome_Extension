console.clear
console.log('This is a popup from EL - 20241210!')

console.log("comment outside searchWord function :)") /* does print */

/** search the current website for words */
const searchWord = () => {
  
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

chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
        target: { tabId: tabs[0].id},
        func: searchWord
    }, (result) => {
                     
        if (result[0].result.oneWord){
          
            console.log("found some flowers!")
            const pageResult = "This webpage has flower info";
            document.getElementById("foundWord").innerText = pageResult; 

        } else {
            console.log("didn't find flowers")
        }
    }
)

}


)

/**Heroku app python */
/*
document.getElementById('process-button').addEventListener('click', async () => {
    try {
        const response = await fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/hello', {
            method: 'GET',
        });

        const result = await response.json();
        document.getElementById('result').textContent = result.message;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').textContent = 'Error connecting to server';
    }
});
*/

// popup.js

document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('process-button');
    const sendInputButton = document.getElementById('send-input-button');
    const resultElement = document.getElementById('result');

    button.addEventListener('click', function() {
        fetchHelloWorld()
            .then(result => {
                resultElement.textContent = result;
            })
            .catch(error => {
                resultElement.textContent = "Error: " + error;
            });
    });

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
                // in jecting script
                chrome.scripting.executeScript( ///)
                    {
                        target: {tabId: tabs[0].id},
                        func: ()=>{
                            return {
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

                    // website URL, text content  -- this doesn't work, gives popup html instead
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
                            const{ url, is_youtube } = python_response.result ; 
                            resultElement.textContent = `Output URL: ${url}\n HasYoutube: ${is_youtube}`;

                        } else {
                            resultElement.textContent = "error: missing " ;
                        }


                        //resultElement.textContent = "Data sent successfully!";
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

function fetchHelloWorld() {
    return fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/hello')  
        .then(response => response.text())
        .then(data => {
            return data;
        });
}

// when button clicked, send to app

/*
function sendDataToFlask(url, content) {
    return fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/send-data', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url, content: content })
    })
    .then(response => response.json())
    .then(data => {
        return data;
    });
}

*/

// sends data to flask and waits for response
// asynchronous because it has to wait for results
async function sendDataToFlask(url, content) {
    try {
        const response = await fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/send-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({url: url, content: content}),
        });

        if(!response.ok){
            throw new Error(`error : ${response.status}`) ;
        }

        const flaskdata = await response.json();
        return flaskdata ;
    } catch (error){
        console.error("error in sending/receiving Flask data", error);
        throw error ; 


    }

}
