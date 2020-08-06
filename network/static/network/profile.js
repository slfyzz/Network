let postTemp = null;
let profileTemp = null;
let paginatorTemp = null;
let currentPage = "";
Handlebars.registerHelper("len", function(value, options) {
    return value.length;
});

Handlebars.registerHelper('ifNEquals', function(arg1, arg2, options) {
    return (arg1 != arg2) ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('ifEquals', function(arg1, arg2, options) {
    return (arg1 == arg2) ? options.fn(this) : options.inverse(this);
});
document.addEventListener('DOMContentLoaded', () => {
    // tempelate for posts
    postTemp = Handlebars.compile(document.querySelector('#postTemps').innerHTML);
    profileTemp = Handlebars.compile(document.querySelector('#profileTemp').innerHTML);
    paginatorTemp = Handlebars.compile(document.querySelector('#paginatorTemp').innerHTML);
    //console.log("HERE");
    loadHome();
    
    if (document.querySelector('#following') !== null)
        document.querySelector('#following').addEventListener('click', loadfollowing);
    
    document.querySelector('#network').addEventListener('click', loadHome);
    document.querySelector('#allPosts').addEventListener('click', loadHome)
    
    if (document.querySelector('#postButton') !== null)
        document.querySelector('#postButton').addEventListener('click', post);

    //loadPosts(1);

});

document.addEventListener('click', e => {

    const targetParent = e.target.parentElement;
    const target = e.target;
    if (targetParent === null || targetParent === undefined)
        return;

    console.log(targetParent);

    // clicking in profile name
    if (targetParent.className.includes("postOwner")) {
        loadProfile(targetParent.dataset.username);
    }

    // clicking in profile 
    else if (targetParent.id === "profile") {
        loadProfile(target.innerHTML.trim());
    }

    // clicking to follow
    else if (target.id === "follow") {
        follow(targetParent.id, target.innerHTML.toLowerCase().trim());
        followers = targetParent.querySelector('#followers');
        if (target.innerHTML === "UnFollow") {
            target.innerHTML = "Follow";
            followers.innerHTML = parseInt(followers.innerHTML.trim()) - 1;
        }
        else{
            target.innerHTML = "UnFollow";
            followers.innerHTML = parseInt(followers.innerHTML.trim()) + 1;
        }
    }
    // clicking to like
    else if (target.className === "like") {
        like(targetParent, target);
    }

    else if (target.className === "edit") {
        editPost(targetParent, target);        
    }
    else if (target.className.includes("paginitem")) {
        if (currentPage === "Home") {
            loadAllPosts(parseInt(target.dataset.link));
        }
        else if (currentPage === "Following") {
            loadAllPosts(parseInt(target.dataset.link), true);
        }
        else if (currentPage === "profile") {
            loadPostsforProfile(parseInt(target.dataset.link));
        } 

    }

});

function loadfollowing() {

    currentPage = "Following";
    console.log("Following");
    document.querySelector('#info').style.display = 'none';
    document.querySelector('#newPostDiv').style.display = 'none';
    loadAllPosts(1, true);
}


function loadHome() {
    currentPage = "Home";
    document.querySelector('#info').style.display = 'none';
    if (document.querySelector('#newPostDiv') !== null)
        document.querySelector('#newPostDiv').style.display = 'block';
    loadAllPosts(1);
}

function loadAllPosts(page, following=false) {

    fetch(`/posts/${following}/${page}`)
    .then(response => response.json())
    .then(data => {
        document.querySelector('#postsContainer').innerHTML = postTemp({'post' : data.posts, 'login' : data.login});
        loadPaginators(data.paginator, page);

        console.log(data);
    });
}

function loadPaginators(paginator, currentPage) {
    pagePaginator = document.querySelector('#pag');
    pagePaginator.innerHTML = "";
    if (currentPage !== 1) {   
        pagePaginator.innerHTML += paginatorTemp({'text': 'Previos', 'val' : currentPage - 1});
    }
    paginator.forEach( num => {
        if (num === currentPage)
            pagePaginator.innerHTML += paginatorTemp({'text': num, 'val' : num, 'active': 'active'});
        else 
            pagePaginator.innerHTML += paginatorTemp({'text': num, 'val' : num});
    });

    if (currentPage !== paginator[paginator.length - 1]) {
        pagePaginator.innerHTML += paginatorTemp({'text': 'Next', 'val' : currentPage + 1});
    }
}


function loadProfile(userName) {
    currentPage = 'profile';
    const profile =  document.querySelector('#info');
    fetch(`/profile/${userName}`)
    .then(response => response.json())
    .then(data => {
        profile.style.display = 'block';
        if (document.querySelector('#newPostDiv') !== null)
            document.querySelector('#newPostDiv').style.display = 'none';
        profile.innerHTML = profileTemp(data);
        loadPostsforProfile(1);
    })
    .catch(e => console.log(e));

}

function loadPostsforProfile(page) {

    userName = document.querySelector("#userName").innerHTML.trim();
    console.log(`profile/${userName}/posts/${page}`)
    fetch(`/profile/${userName}/posts/${page}`)
    .then(response => response.json())
    .then(data => {
        const posts = data.posts;
        document.querySelector('#postsContainer').innerHTML = postTemp({'post' : posts, 'login' : data.login});
        loadPaginators(data.paginator, page);

    })
    .catch(e => console.log(e));

}

function follow(user, follow) {

    console.log(follow);
    fetch(`/${follow}`, {
        method:'PUT',
        body:JSON.stringify({
            user : user            
        })
    })
    .then(response => console.log(response.json()))
    .catch(e => console.log(e));
}


function post() {

    const postText = document.querySelector('#newPost').value;
    console.log("postText: " + postText);
    if (postText === "")
        return;
    
    fetch('/post', {
        method : 'POST',
        body : JSON.stringify({
            post : postText
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.querySelector('#newPost').value = "";
        loadAllPosts(1);
    })
    .catch(e => console.log(e));
}

function like(targetParent, target) {

    grandParent = targetParent.parentElement.parentElement;
    if (grandParent === undefined) {
        console.log("ERROR");
        return;
    }

    idPost = grandParent.id;

    fetch('/like', {
        method : 'PUT',
        body : JSON.stringify({
            postId : idPost  
        })
    })
    .then(response => {
        console.log(response.json());
        let likes = parseInt(targetParent.querySelector('.numOfLikes').innerHTML);
        if (target.innerHTML.trim() === "Unlike") { 
            target.innerHTML = "Like";
            targetParent.querySelector('.numOfLikes').innerHTML = Math.max(likes - 1, 0);
        }
        else {
            target.innerHTML = "Unlike";
            targetParent.querySelector('.numOfLikes').innerHTML = likes + 1;
        }
    })
    .catch(e => console.log(e));
}
function editPost(post, edit) {

    plainText = post.querySelector('.editPost');
    postBody = post.querySelector('.postBody');

    if (edit.innerHTML.trim() === "Edit") {
        plainText.style.display = 'block';
        plainText.value = postBody.innerHTML;

        postBody.style.display = 'none';
        edit.innerHTML = 'Save';
    }
    else {

        if (plainText.value.length === 0)
            return;

        fetch('/editPost', {
            method : 'PUT',
            body : JSON.stringify({
                'id' : post.id,
                'body' : plainText.value 
            })
        })
        .then(response => {
            console.log(response.json());
            postBody.style.display = 'block';
            postBody.innerHTML = plainText.value;
            plainText.style.display = 'none';
            edit.innerHTML = 'Edit';
        })
        .catch(e => console.log(e));
    }
}