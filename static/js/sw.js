self.addEventListener('push', function (event) {
    const data = event.data ? event.data.json() : {};

    self.registration.showNotification(data.title || 'Alerta', {
        body: data.body || '',
    });
});
