import { Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  return (
    <Main>
      <MetaTags>
        <title>Технологии</title>
        <meta name="description" content="Фудграм — Технологии проекта" />
        <meta property="og:title" content="Технологии" />
      </MetaTags>

      <Container>
        <div className={styles.page}>
          <h1 className={styles.title}>Технологии</h1>

          <section className={styles.section}>
            <h2 className={styles.subtitle}>
              Backend и архитектура проекта
            </h2>

            <p className={styles.text}>
              В рамках проекта был разработан backend с нуля.
              Backend реализован на <strong>Django</strong> с использованием
              <strong> Django REST Framework</strong> и представляет собой
              REST API для работы с рецептами, пользователями и
              пользовательскими действиями.
            </p>

            <p className={styles.text}>
              В backend-части проекта реализованы:
            </p>

            <ul className={styles.list}>
              <li>собственная модель пользователей на базе AbstractUser</li>
              <li>аутентификация и авторизация по токенам (Djoser)</li>
              <li>CRUD-операции для рецептов, ингредиентов и тегов</li>
              <li>фильтрация, поиск и пагинация данных</li>
              <li>загрузка и хранение изображений</li>
              <li>работа с избранным и списком покупок</li>
              <li>разграничение прав доступа и защита эндпоинтов</li>
            </ul>

            <p className={styles.text}>
              Backend взаимодействует с frontend-приложением через REST API
              и развёрнут в Docker-контейнерах с использованием
              <strong> PostgreSQL</strong>, <strong>Gunicorn</strong> и
              <strong> Nginx</strong>.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.subtitle}>
              Основные технологии проекта
            </h2>

            <ul className={styles.list}>
              <li>Python</li>
              <li>Django</li>
              <li>Django REST Framework</li>
              <li>Djoser</li>
              <li>PostgreSQL</li>
              <li>Docker</li>
              <li>Nginx</li>
            </ul>
          </section>
        </div>
      </Container>
    </Main>
  )
}

export default Technologies
