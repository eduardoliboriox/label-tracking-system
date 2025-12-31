async function registrarPush() {
    if (!("serviceWorker" in navigator)) {
        console.log("Service Worker não suportado");
        return;
    }

    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
        console.log("Permissão negada");
        return;
    }

    const register = await navigator.serviceWorker.register("/static/sw.js");

    const subscription = await register.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: VAPID_PUBLIC_KEY
    });

    await fetch("/api/push/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(subscription)
    });

    console.log("🔔 Push registrado com sucesso");
}
