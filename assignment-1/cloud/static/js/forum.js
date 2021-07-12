var hello = 0

function edit_post(post_id, subject, message, img) {
    var div = document.getElementById("message-post-area-id")
    div.removeAttribute('hidden')
    document.getElementById('message-post-area-post-id').value = post_id
    document.getElementById('message-post-area-subject').value = subject
    document.getElementById('message-post-area-message').value = message

}

function all_posts() {
    fetch('/forum/all-posts')
        .then(
            function (response) {
                if (response.status !== 200) {
                    console.log('Looks like there was a problem. Status Code: ' +
                        response.status);
                    return;
                }
                // Examine the text in the response
                response.json().then(function (data) {
                    console.log(data);
                    console.log("DATA OVER")
                    hello = data;
                    let counter = 0
                    for (var key in hello) {
                        if (hello.hasOwnProperty(key)) {
                            console.log(key + " -> " + hello[key]);
                            console.log(counter)
                            if (counter === 10) {
                                break
                            }
                            display_all_post(hello[key].creator, hello[key].subject, hello[key].message, hello[key].img_url, hello[key].time, hello[key].creator_img)
                            counter++
                        } else
                            console.log("Not present")
                    }
                    console.log()
                });
            }
        )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });

}

function display_all_post(creator, subject, message, img_url, time, creator_url) {
    var mainDiv = document.createElement("div")
    var leftDiv = document.createElement("div")
    var rightDiv = document.createElement("div")
    mainDiv.className = "post-container"
    mainDiv.style.display = "flex";
    mainDiv.style.flexDirection = "row";
    mainDiv.style.justifyContent = "space-around";
    mainDiv.style.boxShadow = "2px 2px 4px #D3D3D3"
    mainDiv.style.margin = "20px 0"
    leftDiv.className = "left-post-container"
    leftDiv.style.width = "25%"
    leftDiv.style.display = "flex";
    leftDiv.style.flexDirection = "column";
    leftDiv.style.alignItems = "center";
    rightDiv.className = "right-post-container"
    rightDiv.style.width = "75%"
    rightDiv.style.display = "flex";
    rightDiv.style.flexDirection = "column";
    var image = document.createElement("img")
    var creatorp = document.createElement("h6")
    var subjectp = document.createElement("h4")
    var messagep = document.createElement("h6")
    var timep = document.createElement("P")
    var creator_image = document.createElement("img")
    creator_image.className = "crop"
    creator_image.src = creator_url
    image.className = "square-crop"
    image.src = img_url
    creatorp.innerText = creator
    subjectp.innerText = subject
    messagep.innerText = message
    timep.innerText = time
    mainDiv.appendChild(leftDiv)
    mainDiv.appendChild(rightDiv)
    mainDiv.appendChild(image)
    leftDiv.appendChild(creator_image)
    leftDiv.appendChild(creatorp)
    rightDiv.appendChild(subjectp)
    rightDiv.appendChild(messagep)
    rightDiv.appendChild(timep)
    document.getElementById("message-display-area").appendChild(mainDiv);

}

function user_posts() {
    fetch('/forum/user-posts')
        .then(
            function (response) {
                if (response.status !== 200) {
                    console.log('Looks like there was a problem. Status Code: ' +
                        response.status);
                    return;
                }

                // Examine the text in the response
                response.json().then(function (data) {
                    console.log(data);
                    console.log("DATA OVER")
                    hello = data
                    console.log("We start here too")
                    for (var key in hello) {
                        if (hello.hasOwnProperty(key)) {
                            console.log(key + " -> " + hello[key]);
                            display_user_post(key, hello[key].creator, hello[key].subject, hello[key].message, hello[key].img_url, hello[key].time, hello[key].creator_img)
                        } else
                            console.log("Not present")
                    }
                    console.log()
                });
            }
        )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });

}

function display_user_post(key, creator, subject, message, img_url, time, creator_url) {
    var mainDiv = document.createElement("div")
    var leftDiv = document.createElement("div")
    var rightDiv = document.createElement("div")
    mainDiv.className = "post-container"
    mainDiv.style.display = "flex";
    mainDiv.style.flexDirection = "row";
    mainDiv.style.justifyContent = "space-around";
    mainDiv.style.boxShadow = "2px 2px 4px #D3D3D3"
    mainDiv.style.margin = "20px 0"
    leftDiv.className = "left-post-container"
    leftDiv.style.width = "25%"
    leftDiv.style.display = "flex";
    leftDiv.style.flexDirection = "column";
    leftDiv.style.alignItems = "center";
    rightDiv.className = "right-post-container"
    rightDiv.style.width = "75%"
    rightDiv.style.display = "flex";
    rightDiv.style.flexDirection = "column";
    var image = document.createElement("img")
    var creatorp = document.createElement("h6")
    var subjectp = document.createElement("h4")
    var messagep = document.createElement("h6")
    var timep = document.createElement("P")
    var creator_image = document.createElement("img")
    creator_image.className = "crop"
    creator_image.src = creator_url
    image.className = "square-crop"
    image.src = img_url
    creatorp.innerText = creator
    subjectp.innerText = subject
    messagep.innerText = message
    timep.innerText = time
    var butt = document.createElement("a")
    butt.href = "#message-post-area-id"
    butt.text = "Edit"
    // butt.href = "#"
    // butt.onclick = "edit_post(this.data - key, this.data - subject, this.data - message, this.data - image)"
    // butt.setAttribute('onclick', 'edit_post(this.data-postid, this.data-subject, this.data-message, this.data-image)')
    butt.setAttribute('data-postid', key)
    butt.setAttribute('data-subject', subject)
    butt.setAttribute('data-message', message)
    butt.setAttribute('data-img', img_url)
    butt.addEventListener('click', function () {
        edit_post(this.getAttribute("data-postid"), this.getAttribute("data-subject"), this.getAttribute("data-message"), this.getAttribute("data-img"));
    });

    mainDiv.appendChild(leftDiv)
    mainDiv.appendChild(rightDiv)
    mainDiv.appendChild(image)
    leftDiv.appendChild(creator_image)
    leftDiv.appendChild(creatorp)
    rightDiv.appendChild(subjectp)
    rightDiv.appendChild(messagep)
    rightDiv.appendChild(timep)
    rightDiv.appendChild(butt)
    document.getElementById("message-display-area").appendChild(mainDiv);
}


if (document.title === "User Page") {
    user_posts()
} else {
    all_posts()
}
