async function sendAction(url, values) {
    const token = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (!token) throw new Error('Войдите в аккаунт и обновите страницу.');

    const response = await fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': token.value, 'Accept': 'application/json'},
        body: new URLSearchParams(values),
    });

    if (response.status === 401) {
        const login = new URL(document.body.dataset.loginUrl, location.origin);
        login.searchParams.set('next', location.pathname + location.search);
        location.assign(login);
        return null;
    }

    if (!response.headers.get('Content-Type')?.includes('application/json')) {
        throw new Error('Ошибка сервера ' + response.status + '. Обновите страницу.');
    }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    return data;
}

async function vote(button) {
    const box = button.closest('.vote-box');
    const arrows = Array.from(box.querySelectorAll('button'));
    const previous = arrows.map(arrow => arrow.disabled);
    arrows.forEach(arrow => { arrow.disabled = true; });

    try {
        const data = await sendAction(box.dataset.voteUrl, {
            id: box.dataset.id, value: button.dataset.value,
        });
        if (!data) return;

        box.querySelector('b').textContent = data.rating;
        for (const arrow of arrows) {
            const value = Number(arrow.dataset.value);
            const selected = value === data.value;
            arrow.disabled = selected;
            arrow.classList.toggle('on', selected && value === 1);
            arrow.classList.toggle('down', selected && value === -1);
            arrow.title = selected ? 'Вы уже поставили эту оценку' : '';
        }
    } catch (error) {
        arrows.forEach((arrow, index) => { arrow.disabled = previous[index]; });
        throw error;
    }
}

async function markCorrect(button) {
    button.disabled = true;
    try {
        const data = await sendAction(button.dataset.correctUrl, {
            question: button.dataset.question, answer: button.dataset.answer,
        });
        if (!data) return;

        const url = new URL(location.href);
        url.searchParams.set('page', '1');
        url.hash = 'answer-' + data.answer;
        history.replaceState(null, '', url);
        location.reload();
    } catch (error) {
        button.disabled = false;
        throw error;
    }
}

document.addEventListener('click', async event => {
    const button = event.target.closest('button[data-value], button[data-correct-url]');
    if (!button || button.disabled) return;

    try {
        if (button.hasAttribute('data-correct-url')) await markCorrect(button);
        else await vote(button);
    } catch (error) {
        alert(error instanceof TypeError ? 'Проверьте соединение и повторите попытку.' : error.message);
    }
});
