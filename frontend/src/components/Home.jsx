import { useNavigate } from 'react-router-dom';
import {Button, Card, CardGroup} from 'react-bootstrap';

function Home() {
    const navigate = useNavigate();

    return (
        <main className="container mt-5 mb-5">
            <h1 className="text-center homeTitle">Добро пожаловать в сервис генерации синтетических данных</h1>
            <p className="text-center homeSubtitle">С помощью нашего сервиса вы можете генерировать структурированные синтетические данные, которые помогут вам в ваших исследованиях и разработках</p>
            <h2 className="text-center mb-4 homeAlgorithmTitle">Алгоритм работы по шагам</h2>
            <CardGroup>
                <Card>
                    {/* <Card.Img variant="top" src="holder.js/100px160" /> */}
                    <Card.Body>
                        <Card.Title>1. Загрузить данные</Card.Title>
                        <Card.Text>
                            Загрузите ваши данные для начала работы.
                        </Card.Text>
                    </Card.Body>
                </Card>
                <Card>
                    <Card.Body>
                        <Card.Title>2. Настроить структуру данных</Card.Title>
                        <Card.Text>
                            Настройте структуру данных в соответствии с вашими требованиями.
                        </Card.Text>
                    </Card.Body>
                </Card>
                <Card>
                    <Card.Body>
                        <Card.Title>3. Настроить генерацию</Card.Title>
                        <Card.Text>
                            Настройте параметры генерации данных.
                        </Card.Text>
                    </Card.Body>
                </Card>
                <Card>
                    <Card.Body>
                        <Card.Title>4. Сгенерировать данные</Card.Title>
                        <Card.Text>
                            Запустите генерацию данных и получите результат.
                        </Card.Text>
                    </Card.Body>
                </Card>
            </CardGroup>
            <div className="d-flex justify-content-center">
                <Button variant="primary" className="mt-3" onClick={()=> navigate('/generators')}>Начать работу</Button>
            </div>
        </main>
    );
}

export default Home;