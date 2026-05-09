import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// Адрес твоего API (Docker пробрасывает порт 8000)
const API_URL = 'http://localhost:8000'

function App() {
  const [view, setView] = useState('form') // 'form' или 'analytics'
  
  // Состояния для формы
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    city: ''
  })
  const [status, setStatus] = useState('')

  // Состояния для аналитики
  const [analytics, setAnalytics] = useState(null)

  // Функция отправки данных
  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('Отправка...')

    try {
      // Формируем данные так, как ждет наш API
      const payload = {
        answers: [
          { question: "Как тебя зовут?", answer: formData.name },
          { question: "Сколько тебе лет?", answer: formData.age },
          { question: "В каком городе ты живёшь?", answer: formData.city }
        ]
      }

      await axios.post(`${API_URL}/survey/submit`, payload)
      setStatus('✅ Успешно отправлено!')
      setFormData({ name: '', age: '', city: '' }) // Очистить форму
    } catch (error) {
      setStatus('❌ Ошибка при отправке')
      console.error(error)
    }
  }

  // Функция загрузки аналитики
  const loadAnalytics = async () => {
    try {
      const res = await axios.get(`${API_URL}/survey/analytics`)
      setAnalytics(res.data)
      setView('analytics')
    } catch (error) {
      console.error(error)
    }
  }

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', fontFamily: 'sans-serif', padding: '20px' }}>
      <h1>📊 Опросник</h1>
      
      {/* Навигация */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => setView('form')} style={{ marginRight: '10px' }}>Заполнить опрос</button>
        <button onClick={loadAnalytics}>Посмотреть статистику</button>
      </div>

      {/* Форма опроса */}
      {view === 'form' && (
        <form onSubmit={handleSubmit} style={{ background: '#f4f4f4', padding: '20px', borderRadius: '8px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label>Имя:</label><br/>
            <input 
              value={formData.name} 
              onChange={e => setFormData({...formData, name: e.target.value})} 
              required 
              style={{ width: '100%', padding: '8px' }}
            />
          </div>
          
          <div style={{ marginBottom: '10px' }}>
            <label>Возраст:</label><br/>
            <input 
              type="number" 
              value={formData.age} 
              onChange={e => setFormData({...formData, age: e.target.value})} 
              required 
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label>Город:</label><br/>
            <input 
              value={formData.city} 
              onChange={e => setFormData({...formData, city: e.target.value})} 
              required 
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <button type="submit" style={{ background: '#007bff', color: 'white', padding: '10px 20px', border: 'none', cursor: 'pointer' }}>
            Отправить
          </button>
          <p style={{ color: status.includes('✅') ? 'green' : 'red' }}>{status}</p>
        </form>
      )}

      {/* Аналитика */}
      {view === 'analytics' && analytics && (
        <div style={{ background: '#e9ecef', padding: '20px', borderRadius: '8px' }}>
          <h2>📈 Статистика</h2>
          
          <h3>По возрасту:</h3>
          <ul>
            {Object.entries(analytics.ages).map(([age, count]) => (
              <li key={age}><b>{age} лет:</b> {count} чел.</li>
            ))}
          </ul>

          <h3>По городам:</h3>
          <ul>
            {Object.entries(analytics.cities).map(([city, count]) => (
              <li key={city}><b>{city}:</b> {count} чел.</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App