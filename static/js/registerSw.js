//check if service workers are supported on the user’s browser before attempting to register a service worker
const registerSw = async () => {
    if ('serviceWorker' in navigator) {
        const reg = await navigator.serviceWorker.register('sw.js');
        initialiseState(reg)

    } else {
        showNotAllowed("You can't send push notifications")
    }
};

// check if a user is eligible to receive push notifications before attempting to subscribe them
const initialiseState = (reg) => {
//Whether or not the user has enabled notifications
    if (!reg.showNotification) {
        showNotAllowed('Showing notifications isn\'t supported');
        return
    }
//Whether or not the user has granted the application permission to display notifications
    if (Notification.permission === 'denied') {
        showNotAllowed('You prevented us from showing notifications');
        return
    }
//Whether or not the browser supports the PushManager API
    if (!'PushManager' in window) {
        showNotAllowed("Push isn't allowed in your browser");
        return
    }
    subscribe(reg);
}

const showNotAllowed = (message) => {
    const button = document.querySelector('form>button');
    button.innerHTML = `${message}`;
    button.setAttribute('disabled', 'true');
};

//Once we ensure that a user is eligible to receive push notifications,
//the next step is to subscribe them using pushManager

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    const outputData = outputArray.map((output, index) => rawData.charCodeAt(index));

    return outputData;
}

const subscribe = async (reg) => {
//Calling the pushManager.getSubscription function returns the data for an active subscription.
//When an active subscription exists, the sendSubData function is called with the subscription info passed in as a parameter.
    const subscription = await reg.pushManager.getSubscription();
    if (subscription) {
        sendSubData(subscription);
        return;
    }

//When no active subscription exists, the VAPID public key, which is Base64 URL-safe encoded, is converted to a Uint8Array
//using the urlB64ToUint8Array function.
    const vapidMeta = document.querySelector('meta[name="vapid-key"]');
    const key = vapidMeta.content;
    const options = {
        userVisibleOnly: true,
        // if key exists, create applicationServerKey property
        ...(key && {applicationServerKey: urlB64ToUint8Array(key)})
    };

//pushManager.subscribe is then called with the VAPID public key and the userVisible value as options.
    const sub = await reg.pushManager.subscribe(options);
    sendSubData(sub)
};

//After successfully subscribing a user, the next step is to send the subscription data to the server.
const sendSubData = async (subscription) => {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();
    const data = {
        status_type: 'subscribe',
        subscription: subscription.toJSON(),
        browser: browser,
    };
//The data will be sent to the webpush/save_information endpoint provided by the django-webpush package.
    const res = await fetch('/webpush/save_information', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'content-type': 'application/json'
        },
        credentials: "include"
    });

    handleResponse(res);
};

const handleResponse = (res) => {
    console.log(res.status);
};

registerSw();