const form = document.getElementById('form');

form.addEventListener('submit', (event) => {
    event.preventDefault(); // Не отправлять форму обычным способом

    // Получить выбранные значения
    const service = document.querySelector('input[name="service"]:checked').value;
    const targetType = document.querySelector('input[name="target_type"]:checked').value;

    // Сформировать URL-адрес для запроса
    const url = `http://127.0.0.1:8000/images/upload?service=${service}&target_type=${targetType}`;

    // Отправить данные на сервер (например, с помощью fetch)
    fetch(url, {
        method: 'POST',
        body: new FormData(form), // Данные формы
    })
    .then(response => {
        // Обработать ответ сервера
    })
    .catch(error => {
        // Обработать ошибку
    });
});