import React, { } from 'react';
import { useNavigate } from 'react-router-dom';
import Auth from './Auth';

import {Container, Nav, Navbar} from 'react-bootstrap';

function Header() {
    const navigate = useNavigate();

    const goToGenerators = () => {
        navigate('/generators');
    };

    const goToHome = () => {
        navigate('/');
    };

    return (
        <header>
            <Navbar expand="lg" className="bg-body-tertiary">
                <Container>
                    <Navbar.Brand style={{ cursor: 'pointer' }} onClick={goToHome}>DataGenerator</Navbar.Brand>
                    <Navbar.Toggle aria-controls="basic-navbar-nav" />
                    <Navbar.Collapse id="basic-navbar-nav" className="justify-content-between">
                        <Nav className="me-auto justify-content-center flex-grow-1 align-items-center">
                            <Nav.Link onClick={goToGenerators}>Генераторы</Nav.Link>
                            {/* <Nav.Link onClick={goToHome}>Синтетические данные</Nav.Link> */}
                        </Nav>
                        <Auth/>
                    </Navbar.Collapse>
                </Container>
            </Navbar>
        </header>
    ); 
}

export default Header;