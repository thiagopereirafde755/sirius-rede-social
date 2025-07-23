-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3308
-- Tempo de geração: 23/07/2025 às 00:33
-- Versão do servidor: 10.4.32-MariaDB
-- Versão do PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `sirius`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `adm`
--

CREATE TABLE `adm` (
  `id` int(11) NOT NULL,
  `user` varchar(50) DEFAULT NULL,
  `senha` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `adm`
--

INSERT INTO `adm` (`id`, `user`, `senha`) VALUES
(1, 'administradorprincipal1', 'scrypt:32768:8:1$vi5KX8sqME2kvGYE$ea3f7579584541022bad06d641d27fec8aac237e4458a483d17cc010e598f06041441870a69b3f179cbef36e9eb2a8e4b93ca724a81d2251e2fa70952b8f422e');

-- --------------------------------------------------------

--
-- Estrutura para tabela `bloqueados`
--

CREATE TABLE `bloqueados` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `bloqueado_id` int(11) NOT NULL,
  `data_bloqueio` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `comentarios`
--

CREATE TABLE `comentarios` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `comentario` text NOT NULL,
  `data_comentario` timestamp NOT NULL DEFAULT current_timestamp(),
  `parent_comment_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `comentarios`
--

INSERT INTO `comentarios` (`id`, `post_id`, `usuario_id`, `comentario`, `data_comentario`, `parent_comment_id`) VALUES
(21, 1, 1, 'AAAAAAAAAAAAAAA', '2025-07-22 14:34:52', NULL),
(24, 9, 2, 'Aaaa', '2025-07-22 18:48:16', NULL),
(25, 9, 2, 'AAAA', '2025-07-22 18:48:20', NULL),
(26, 9, 2, 'Aaaaa', '2025-07-22 18:48:23', NULL),
(28, 11, 2, 'Aaa', '2025-07-22 19:11:18', NULL),
(29, 11, 2, 'AAA', '2025-07-22 19:11:22', 28),
(30, 9, 1, 'a', '2025-07-22 20:19:59', NULL);

-- --------------------------------------------------------

--
-- Estrutura para tabela `comentario_mencoes`
--

CREATE TABLE `comentario_mencoes` (
  `id` int(11) NOT NULL,
  `comentario_id` int(11) NOT NULL,
  `user_mencionado_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `curtidas`
--

CREATE TABLE `curtidas` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `data` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `curtidas`
--

INSERT INTO `curtidas` (`id`, `post_id`, `usuario_id`, `data`) VALUES
(19, 9, 1, '2025-07-22 11:36:09'),
(20, 9, 2, '2025-07-22 15:48:11'),
(22, 11, 2, '2025-07-22 16:04:13'),
(23, 1, 2, '2025-07-22 16:11:04'),
(24, 1, 1, '2025-07-22 17:16:38');

-- --------------------------------------------------------

--
-- Estrutura para tabela `denuncias`
--

CREATE TABLE `denuncias` (
  `id` int(11) NOT NULL,
  `tipo` enum('usuario','post','comentario','mensagem') NOT NULL,
  `id_alvo` int(11) NOT NULL,
  `id_denunciante` int(11) NOT NULL,
  `motivo` text NOT NULL,
  `data_denuncia` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('pendente','em_analise','resolvido','ignorado') NOT NULL DEFAULT 'pendente',
  `observacoes_admin` text DEFAULT NULL,
  `descricao` varchar(80) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `denuncias`
--

INSERT INTO `denuncias` (`id`, `tipo`, `id_alvo`, `id_denunciante`, `motivo`, `data_denuncia`, `status`, `observacoes_admin`, `descricao`) VALUES
(16, 'mensagem', 56, 2, 'spam', '2025-07-22 21:52:55', 'pendente', NULL, 'Aaa');

-- --------------------------------------------------------

--
-- Estrutura para tabela `hashtags`
--

CREATE TABLE `hashtags` (
  `id` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `hashtags`
--

INSERT INTO `hashtags` (`id`, `nome`) VALUES
(1, '#cr7'),
(4, '#goat');

-- --------------------------------------------------------

--
-- Estrutura para tabela `historico_pesquisa_post`
--

CREATE TABLE `historico_pesquisa_post` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `termo` varchar(255) NOT NULL,
  `criado_em` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `historico_pesquisa_post`
--

INSERT INTO `historico_pesquisa_post` (`id`, `usuario_id`, `termo`, `criado_em`) VALUES
(1, 1, 'Cr7', '2025-07-21 18:46:26'),
(2, 1, '#cr7', '2025-07-22 11:45:32'),
(10, 2, 'Hala', '2025-07-22 16:07:41'),
(11, 2, '#goat', '2025-07-22 16:08:25');

-- --------------------------------------------------------

--
-- Estrutura para tabela `historico_pesquisa_procurar_usuarios`
--

CREATE TABLE `historico_pesquisa_procurar_usuarios` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `usuario_pesquisado_id` int(11) NOT NULL,
  `data_pesquisa` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `historico_pesquisa_procurar_usuarios`
--

INSERT INTO `historico_pesquisa_procurar_usuarios` (`id`, `usuario_id`, `usuario_pesquisado_id`, `data_pesquisa`) VALUES
(24, 1, 1, '2025-07-22 18:46:40'),
(25, 1, 2, '2025-07-22 18:46:46');

-- --------------------------------------------------------

--
-- Estrutura para tabela `mensagens`
--

CREATE TABLE `mensagens` (
  `id` int(11) NOT NULL,
  `id_remetente` int(11) NOT NULL,
  `id_destinatario` int(11) NOT NULL,
  `post_id` int(11) DEFAULT NULL,
  `mensagem` text DEFAULT NULL,
  `data_envio` timestamp NOT NULL DEFAULT current_timestamp(),
  `lida` tinyint(1) DEFAULT 0,
  `caminho_arquivo` varchar(255) DEFAULT NULL,
  `id_mensagem_respondida` int(11) DEFAULT NULL,
  `data_visualizacao` timestamp NULL DEFAULT NULL,
  `public_id` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `mensagens`
--

INSERT INTO `mensagens` (`id`, `id_remetente`, `id_destinatario`, `post_id`, `mensagem`, `data_envio`, `lida`, `caminho_arquivo`, `id_mensagem_respondida`, `data_visualizacao`, `public_id`) VALUES
(42, 2, 1, NULL, 'Aaaaaa', '2025-07-22 18:48:48', 0, NULL, 0, '2025-07-22 18:48:49', NULL),
(43, 2, 1, NULL, 'Aaaa', '2025-07-22 18:48:53', 0, NULL, 0, '2025-07-22 18:48:53', NULL),
(44, 2, 1, NULL, 'Aaaa', '2025-07-22 18:48:57', 0, NULL, 0, '2025-07-22 18:48:57', NULL),
(45, 2, 1, NULL, 'Aaaa', '2025-07-22 18:49:03', 0, NULL, 0, '2025-07-22 18:49:03', NULL),
(46, 2, 1, NULL, 'Aaaaa', '2025-07-22 18:49:24', 0, NULL, 42, '2025-07-22 18:49:25', NULL),
(47, 2, 1, NULL, 'Aaa', '2025-07-22 18:49:28', 0, NULL, 44, '2025-07-22 18:49:29', NULL),
(48, 2, 1, NULL, 'aaaaaa', '2025-07-22 18:49:33', 0, NULL, 0, '2025-07-22 18:49:33', NULL),
(49, 2, 1, NULL, 'A', '2025-07-22 18:49:56', 0, NULL, 0, '2025-07-22 18:49:57', NULL),
(50, 2, 1, NULL, 'aa', '2025-07-22 18:50:14', 0, NULL, 0, '2025-07-22 18:50:15', NULL),
(51, 2, 1, NULL, 'Adhdu', '2025-07-22 18:50:29', 0, NULL, 0, '2025-07-22 18:50:29', NULL),
(52, 2, 1, NULL, 'AAaa', '2025-07-22 18:50:41', 0, NULL, 0, '2025-07-22 18:50:41', NULL),
(53, 1, 2, NULL, 'ccccccccccccccc', '2025-07-22 18:50:49', 0, NULL, 0, '2025-07-22 18:50:50', NULL),
(54, 1, 2, NULL, ',k,k,k,', '2025-07-22 18:50:59', 0, NULL, 0, '2025-07-22 18:51:00', NULL),
(55, 1, 2, NULL, 'lll', '2025-07-22 18:51:04', 0, NULL, 0, '2025-07-22 18:51:04', NULL),
(56, 1, 2, NULL, 'kkk', '2025-07-22 18:51:12', 0, NULL, 0, '2025-07-22 18:51:12', NULL),
(57, 2, 1, NULL, NULL, '2025-07-22 18:51:34', 0, 'https://res.cloudinary.com/dv5rk3ibv/image/upload/v1753210293/chat/fotos/ukvlobmsz7nhdascnc91.jpg', 0, '2025-07-22 18:51:35', 'chat/fotos/ukvlobmsz7nhdascnc91'),
(58, 2, 1, NULL, 'Aaa', '2025-07-22 18:52:14', 0, NULL, 0, '2025-07-22 18:52:15', NULL),
(59, 2, 1, NULL, 'Aa', '2025-07-22 19:27:05', 0, NULL, 0, '2025-07-22 20:14:21', NULL),
(60, 2, 1, NULL, 'H', '2025-07-22 19:27:42', 0, NULL, 0, '2025-07-22 20:14:21', NULL),
(61, 2, 1, NULL, 'Hjh', '2025-07-22 19:28:18', 0, NULL, 0, '2025-07-22 20:14:21', NULL),
(62, 1, 2, NULL, 'a', '2025-07-22 20:14:24', 0, NULL, 0, NULL, NULL),
(63, 1, 2, NULL, 'a', '2025-07-22 20:14:26', 0, NULL, 0, NULL, NULL),
(64, 1, 2, NULL, 'a', '2025-07-22 20:14:27', 0, NULL, 0, NULL, NULL);

-- --------------------------------------------------------

--
-- Estrutura para tabela `notificacoes`
--

CREATE TABLE `notificacoes` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `tipo` enum('curtida','comentario','seguidor','mencao','aceite_pedido','pedido_seguir','resposta','post_removido','comentario_removido','mensagem_removida','republicado') NOT NULL,
  `origem_usuario_id` int(11) DEFAULT NULL,
  `post_id` int(11) DEFAULT NULL,
  `data_notificacao` timestamp NOT NULL DEFAULT current_timestamp(),
  `lida` tinyint(1) DEFAULT 0,
  `comentario_id` int(11) DEFAULT NULL,
  `lida_push` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `notificacoes`
--

INSERT INTO `notificacoes` (`id`, `usuario_id`, `tipo`, `origem_usuario_id`, `post_id`, `data_notificacao`, `lida`, `comentario_id`, `lida_push`) VALUES
(4, 2, 'seguidor', 1, NULL, '2025-07-22 18:46:51', 1, NULL, 1),
(5, 1, 'seguidor', 2, NULL, '2025-07-22 18:47:37', 1, NULL, 1),
(7, 1, 'curtida', 2, 9, '2025-07-22 18:48:11', 1, NULL, 1),
(8, 1, 'comentario', 2, 9, '2025-07-22 18:48:16', 1, 24, 1),
(9, 1, 'comentario', 2, 9, '2025-07-22 18:48:20', 1, 25, 1),
(10, 1, 'comentario', 2, 9, '2025-07-22 18:48:23', 1, 26, 1),
(13, 1, 'republicado', 2, 9, '2025-07-22 18:53:20', 1, NULL, 1),
(15, 1, 'seguidor', 2, NULL, '2025-07-22 19:05:51', 1, NULL, 1),
(16, 2, 'republicado', 1, 12, '2025-07-22 19:08:39', 1, NULL, 1),
(18, 1, 'republicado', 2, 1, '2025-07-22 19:11:03', 1, NULL, 1),
(19, 1, 'curtida', 2, 1, '2025-07-22 19:11:04', 1, NULL, 1);

-- --------------------------------------------------------

--
-- Estrutura para tabela `pedidos_seguir`
--

CREATE TABLE `pedidos_seguir` (
  `id` int(11) NOT NULL,
  `id_solicitante` int(11) NOT NULL,
  `id_destino` int(11) NOT NULL,
  `data_pedido` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `pesquisas`
--

CREATE TABLE `pesquisas` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `termo` varchar(255) NOT NULL,
  `data_pesquisa` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `pesquisas`
--

INSERT INTO `pesquisas` (`id`, `usuario_id`, `termo`, `data_pesquisa`) VALUES
(1, 1, 'aa', '2025-07-07 21:17:04'),
(2, 1, 'cr7', '2025-07-07 21:17:26'),
(3, 1, 'ad', '2025-07-07 21:31:41');

-- --------------------------------------------------------

--
-- Estrutura para tabela `posts`
--

CREATE TABLE `posts` (
  `id` int(11) NOT NULL,
  `users_id` int(11) NOT NULL,
  `conteudo` varchar(280) DEFAULT NULL,
  `imagem` varchar(500) DEFAULT NULL,
  `video` varchar(500) DEFAULT NULL,
  `data_postagem` timestamp NOT NULL DEFAULT current_timestamp(),
  `score_ml` float DEFAULT 0,
  `imagem_public_id` varchar(255) DEFAULT NULL,
  `video_public_id` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `posts`
--

INSERT INTO `posts` (`id`, `users_id`, `conteudo`, `imagem`, `video`, `data_postagem`, `score_ml`, `imagem_public_id`, `video_public_id`) VALUES
(1, 1, '#cr7', NULL, NULL, '2025-07-21 21:45:20', 0, NULL, NULL),
(9, 1, '#cr7 aaaaa', NULL, NULL, '2025-07-22 14:36:00', 0, NULL, NULL),
(11, 2, '#cr7 #goat Siuuu', NULL, 'https://res.cloudinary.com/dv5rk3ibv/video/upload/v1753211007/posts/videos/imglopewp2vjevlozfz2.mp4', '2025-07-22 19:03:29', 0, NULL, 'posts/videos/imglopewp2vjevlozfz2'),
(12, 2, '#cr7 Hala madrid ', NULL, 'https://res.cloudinary.com/dv5rk3ibv/video/upload/v1753211109/posts/videos/rfndetvxsvf8iatbxem8.mp4', '2025-07-22 19:05:11', 0, NULL, 'posts/videos/rfndetvxsvf8iatbxem8'),
(13, 2, 'Teste', 'https://res.cloudinary.com/dv5rk3ibv/image/upload/v1753211845/posts/fotos/uj2wgldhjlfu5qojk0gt.jpg', 'https://res.cloudinary.com/dv5rk3ibv/video/upload/v1753211847/posts/videos/jl3fjgum39wzhhnaajxn.mp4', '2025-07-22 19:17:28', 0, 'posts/fotos/uj2wgldhjlfu5qojk0gt', 'posts/videos/jl3fjgum39wzhhnaajxn');

-- --------------------------------------------------------

--
-- Estrutura para tabela `posts_republicados`
--

CREATE TABLE `posts_republicados` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `data` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `posts_republicados`
--

INSERT INTO `posts_republicados` (`id`, `post_id`, `usuario_id`, `data`) VALUES
(144, 1, 1, '2025-07-22 11:35:34'),
(151, 9, 1, '2025-07-22 11:45:36'),
(154, 9, 2, '2025-07-22 15:53:20'),
(158, 11, 2, '2025-07-22 16:08:35'),
(159, 12, 1, '2025-07-22 16:08:39'),
(163, 1, 2, '2025-07-22 16:11:03'),
(166, 12, 2, '2025-07-22 16:14:50');

-- --------------------------------------------------------

--
-- Estrutura para tabela `posts_salvos`
--

CREATE TABLE `posts_salvos` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `data` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `posts_salvos`
--

INSERT INTO `posts_salvos` (`id`, `usuario_id`, `post_id`, `data`) VALUES
(29, 1, 1, '2025-07-22 11:35:37'),
(36, 1, 9, '2025-07-22 11:45:37'),
(37, 2, 9, '2025-07-22 15:53:21'),
(39, 2, 11, '2025-07-22 16:12:01');

-- --------------------------------------------------------

--
-- Estrutura para tabela `post_hashtags`
--

CREATE TABLE `post_hashtags` (
  `post_id` int(11) NOT NULL,
  `hashtag_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `post_hashtags`
--

INSERT INTO `post_hashtags` (`post_id`, `hashtag_id`) VALUES
(1, 1),
(9, 1),
(11, 1),
(11, 4),
(12, 1);

-- --------------------------------------------------------

--
-- Estrutura para tabela `post_mencoes`
--

CREATE TABLE `post_mencoes` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `user_mencionado_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `recuperacao_senha`
--

CREATE TABLE `recuperacao_senha` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `codigo` varchar(10) NOT NULL,
  `criado_em` datetime NOT NULL,
  `utilizado_em` datetime DEFAULT NULL,
  `expirado_em` datetime DEFAULT NULL,
  `ip_criacao` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `seguindo`
--

CREATE TABLE `seguindo` (
  `id_seguidor` int(11) NOT NULL,
  `id_seguindo` int(11) NOT NULL,
  `data_seguindo` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `seguindo`
--

INSERT INTO `seguindo` (`id_seguidor`, `id_seguindo`, `data_seguindo`) VALUES
(1, 2, '2025-07-22 18:46:51'),
(2, 1, '2025-07-22 19:05:51');

-- --------------------------------------------------------

--
-- Estrutura para tabela `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `nome` varchar(60) NOT NULL,
  `username` varchar(12) NOT NULL,
  `email` varchar(400) NOT NULL,
  `data_nascimento` date DEFAULT NULL,
  `senha` varchar(255) NOT NULL,
  `fotos_perfil` varchar(255) DEFAULT NULL,
  `bio` varchar(150) DEFAULT NULL,
  `codigo_user` varchar(50) DEFAULT NULL,
  `codigo_user_gerado_em` datetime DEFAULT NULL,
  `conta_confirmada` tinyint(1) NOT NULL DEFAULT 0,
  `foto_capa` varchar(355) DEFAULT NULL,
  `perfil_publico` tinyint(1) DEFAULT 1,
  `tema` enum('claro','escuro') DEFAULT 'claro',
  `comentarios_publicos` enum('todos','privado','seguidores_mutuos') NOT NULL DEFAULT 'todos',
  `visibilidade_seguidores` enum('publico','privado') NOT NULL DEFAULT 'publico',
  `ultima_atividade` datetime DEFAULT NULL,
  `online` tinyint(1) DEFAULT 0,
  `audio_notificacoes` tinyint(1) NOT NULL DEFAULT 1,
  `audio_notificacoes_mensagem` tinyint(1) NOT NULL DEFAULT 1,
  `curtidas_publicas` tinyint(1) NOT NULL DEFAULT 1,
  `modo_status` enum('normal','ausente') NOT NULL DEFAULT 'normal',
  `data_cadastro` datetime NOT NULL DEFAULT current_timestamp(),
  `suspenso` tinyint(1) NOT NULL DEFAULT 0,
  `token_sessao` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `users`
--

INSERT INTO `users` (`id`, `nome`, `username`, `email`, `data_nascimento`, `senha`, `fotos_perfil`, `bio`, `codigo_user`, `codigo_user_gerado_em`, `conta_confirmada`, `foto_capa`, `perfil_publico`, `tema`, `comentarios_publicos`, `visibilidade_seguidores`, `ultima_atividade`, `online`, `audio_notificacoes`, `audio_notificacoes_mensagem`, `curtidas_publicas`, `modo_status`, `data_cadastro`, `suspenso`, `token_sessao`) VALUES
(1, 'Thiago Pereira', 'Thiagofde_7', 'thiagopereirafde755@gmail.com', '2008-03-30', 'scrypt:32768:8:1$PmJAesjjMMrSPWle$48491dca9628699805c0df0636419e78136861b8d54d8e47dcb805d570054f4d6932f272996a74c870f8cf6780d158b53292d7295cc89994724cc27809aca142', NULL, NULL, 'UKLXJF', '2025-07-21 18:20:09', 1, NULL, 1, 'claro', 'todos', 'publico', '2025-07-22 17:54:08', 0, 1, 1, 1, 'normal', '2025-07-21 18:20:09', 0, '998bd2ef-64a7-47d9-9d0f-0dafecebed79'),
(2, 'Thiago de Souza Pereira', 'thiagofde755', 'thiagofde.ps4@gmail.com', '2008-03-30', 'scrypt:32768:8:1$GtVOskINwYBaIGK0$1c3f819ea4905df57db5fed5fad599ba1e0102c29d954c26424648c64f27d490592c70fce9f76567e145327af75f1a902384c400e62e48ff9ab89bf36db7f815', 'https://res.cloudinary.com/dv5rk3ibv/image/upload/v1753210692/foto_perfil/perfil_2_20250722155813.jpg', NULL, 'LXIC8M', '2025-07-22 15:45:44', 1, NULL, 1, 'escuro', 'todos', 'publico', '2025-07-22 16:37:04', 1, 1, 1, 1, 'normal', '2025-07-22 15:45:45', 0, NULL);

-- --------------------------------------------------------

--
-- Estrutura para tabela `visualizacoes`
--

CREATE TABLE `visualizacoes` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `data_visualizacao` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `visualizacoes`
--

INSERT INTO `visualizacoes` (`id`, `usuario_id`, `post_id`, `data_visualizacao`) VALUES
(1, 1, 1, '2025-07-21 18:45:21'),
(2, 1, 1, '2025-07-21 18:45:37'),
(3, 1, 1, '2025-07-21 18:45:53'),
(4, 1, 1, '2025-07-21 18:46:09'),
(5, 1, 1, '2025-07-21 18:46:26'),
(6, 1, 1, '2025-07-21 18:46:31'),
(7, 1, 1, '2025-07-21 18:46:35'),
(8, 1, 1, '2025-07-21 18:46:44'),
(9, 1, 1, '2025-07-21 18:46:55'),
(10, 1, 1, '2025-07-21 18:47:10'),
(11, 1, 1, '2025-07-21 18:47:13'),
(12, 1, 1, '2025-07-21 18:47:22'),
(13, 1, 1, '2025-07-21 18:47:28'),
(14, 1, 1, '2025-07-21 18:47:30'),
(15, 1, 1, '2025-07-21 18:47:38'),
(16, 1, 1, '2025-07-21 18:47:41'),
(17, 1, 1, '2025-07-21 18:47:45'),
(18, 1, 1, '2025-07-21 18:47:50'),
(19, 1, 1, '2025-07-21 18:48:07'),
(20, 1, 1, '2025-07-21 18:48:12'),
(21, 1, 1, '2025-07-21 18:50:41'),
(22, 1, 1, '2025-07-21 18:51:02'),
(23, 1, 1, '2025-07-21 18:51:24'),
(24, 1, 1, '2025-07-21 18:52:28'),
(25, 1, 1, '2025-07-21 18:52:36'),
(26, 1, 1, '2025-07-21 18:52:41'),
(27, 1, 1, '2025-07-21 18:53:01'),
(28, 1, 1, '2025-07-21 18:53:56'),
(29, 1, 1, '2025-07-21 18:54:16'),
(30, 1, 1, '2025-07-21 18:54:44'),
(31, 1, 1, '2025-07-21 18:55:27'),
(32, 1, 1, '2025-07-21 18:56:58'),
(33, 1, 1, '2025-07-21 18:57:40'),
(34, 1, 1, '2025-07-21 18:57:51'),
(3193, 1, 1, '2025-07-22 11:14:06'),
(3194, 1, 1, '2025-07-22 11:14:21'),
(3195, 1, 1, '2025-07-22 11:14:37'),
(3196, 1, 1, '2025-07-22 11:16:01'),
(3197, 1, 1, '2025-07-22 11:16:46'),
(3198, 1, 1, '2025-07-22 11:18:31'),
(3199, 1, 1, '2025-07-22 11:18:57'),
(3200, 1, 1, '2025-07-22 11:19:00'),
(3201, 1, 1, '2025-07-22 11:19:06'),
(3202, 1, 1, '2025-07-22 11:20:18'),
(3203, 1, 1, '2025-07-22 11:20:56'),
(3204, 1, 1, '2025-07-22 11:23:22'),
(3205, 1, 1, '2025-07-22 11:32:08'),
(3206, 1, 1, '2025-07-22 11:34:37'),
(3207, 1, 1, '2025-07-22 11:35:51'),
(3208, 1, 9, '2025-07-22 11:36:01'),
(3209, 1, 1, '2025-07-22 11:36:01'),
(3210, 1, 9, '2025-07-22 11:36:39'),
(3211, 1, 1, '2025-07-22 11:36:39'),
(3212, 1, 9, '2025-07-22 11:36:44'),
(3213, 1, 9, '2025-07-22 11:36:45'),
(3214, 1, 1, '2025-07-22 11:36:45'),
(3215, 1, 1, '2025-07-22 11:36:50'),
(3216, 1, 9, '2025-07-22 11:36:50'),
(3217, 1, 1, '2025-07-22 11:36:52'),
(3218, 1, 9, '2025-07-22 11:36:52'),
(3219, 1, 1, '2025-07-22 11:37:07'),
(3220, 1, 9, '2025-07-22 11:37:07'),
(3221, 1, 1, '2025-07-22 11:37:29'),
(3222, 1, 9, '2025-07-22 11:37:29'),
(3223, 1, 9, '2025-07-22 11:38:06'),
(3224, 1, 1, '2025-07-22 11:38:07'),
(3225, 1, 9, '2025-07-22 11:41:04'),
(3226, 1, 9, '2025-07-22 11:41:49'),
(3227, 1, 1, '2025-07-22 11:41:49'),
(3229, 1, 9, '2025-07-22 11:41:59'),
(3231, 1, 9, '2025-07-22 11:45:26'),
(3232, 1, 1, '2025-07-22 11:45:26'),
(3233, 1, 9, '2025-07-22 11:45:28'),
(3234, 1, 1, '2025-07-22 11:45:28'),
(3235, 1, 9, '2025-07-22 11:45:29'),
(3236, 1, 1, '2025-07-22 11:45:29'),
(3237, 1, 9, '2025-07-22 11:45:32'),
(3238, 1, 1, '2025-07-22 11:45:32'),
(3239, 1, 9, '2025-07-22 11:45:33'),
(3240, 1, 1, '2025-07-22 11:45:33'),
(3243, 1, 9, '2025-07-22 13:25:00'),
(3244, 1, 1, '2025-07-22 13:25:03'),
(3245, 1, 9, '2025-07-22 13:25:08'),
(3246, 1, 1, '2025-07-22 13:25:09'),
(3247, 1, 9, '2025-07-22 14:25:10'),
(3248, 1, 1, '2025-07-22 14:25:11'),
(3249, 1, 9, '2025-07-22 14:25:38'),
(3250, 1, 9, '2025-07-22 14:25:48'),
(3251, 1, 1, '2025-07-22 14:25:49'),
(3252, 1, 9, '2025-07-22 15:44:07'),
(3253, 1, 9, '2025-07-22 15:46:42'),
(3254, 1, 1, '2025-07-22 15:46:42'),
(3255, 2, 9, '2025-07-22 15:47:36'),
(3256, 2, 9, '2025-07-22 15:47:38'),
(3257, 2, 1, '2025-07-22 15:47:42'),
(3258, 2, 9, '2025-07-22 15:48:02'),
(3259, 2, 9, '2025-07-22 15:53:17'),
(3260, 2, 1, '2025-07-22 15:53:17'),
(3261, 1, 9, '2025-07-22 15:53:26'),
(3262, 1, 1, '2025-07-22 15:53:26'),
(3263, 2, 11, '2025-07-22 16:03:34'),
(3264, 2, 12, '2025-07-22 16:05:13'),
(3265, 2, 11, '2025-07-22 16:05:15'),
(3266, 2, 1, '2025-07-22 16:05:44'),
(3267, 2, 9, '2025-07-22 16:05:44'),
(3268, 2, 9, '2025-07-22 16:05:50'),
(3269, 2, 9, '2025-07-22 16:05:51'),
(3270, 1, 12, '2025-07-22 16:06:09'),
(3271, 2, 1, '2025-07-22 16:06:16'),
(3272, 2, 1, '2025-07-22 16:06:20'),
(3273, 2, 9, '2025-07-22 16:06:20'),
(3274, 2, 11, '2025-07-22 16:06:25'),
(3275, 2, 12, '2025-07-22 16:06:27'),
(3276, 2, 12, '2025-07-22 16:07:43'),
(3277, 2, 11, '2025-07-22 16:07:47'),
(3278, 2, 12, '2025-07-22 16:08:16'),
(3279, 2, 11, '2025-07-22 16:08:26'),
(3280, 2, 12, '2025-07-22 16:08:47'),
(3281, 2, 9, '2025-07-22 16:09:02'),
(3282, 2, 12, '2025-07-22 16:09:03'),
(3283, 2, 9, '2025-07-22 16:09:04'),
(3284, 2, 12, '2025-07-22 16:09:06'),
(3285, 2, 9, '2025-07-22 16:09:07'),
(3286, 2, 1, '2025-07-22 16:09:08'),
(3287, 2, 12, '2025-07-22 16:09:31'),
(3288, 2, 11, '2025-07-22 16:09:31'),
(3289, 2, 9, '2025-07-22 16:10:10'),
(3290, 2, 9, '2025-07-22 16:10:47'),
(3291, 2, 1, '2025-07-22 16:10:47'),
(3292, 2, 9, '2025-07-22 16:10:58'),
(3293, 2, 1, '2025-07-22 16:10:58'),
(3294, 2, 11, '2025-07-22 16:11:07'),
(3295, 2, 12, '2025-07-22 16:11:17'),
(3296, 2, 11, '2025-07-22 16:11:52'),
(3297, 2, 9, '2025-07-22 16:11:52'),
(3298, 2, 1, '2025-07-22 16:11:56'),
(3299, 2, 11, '2025-07-22 16:12:04'),
(3300, 2, 9, '2025-07-22 16:12:06'),
(3301, 2, 11, '2025-07-22 16:12:11'),
(3302, 2, 9, '2025-07-22 16:12:31'),
(3303, 2, 11, '2025-07-22 16:12:31'),
(3304, 2, 1, '2025-07-22 16:12:39'),
(3305, 2, 12, '2025-07-22 16:12:39'),
(3306, 2, 12, '2025-07-22 16:15:25'),
(3307, 2, 12, '2025-07-22 16:15:52'),
(3308, 2, 11, '2025-07-22 16:16:12'),
(3309, 2, 9, '2025-07-22 16:16:17'),
(3310, 2, 11, '2025-07-22 16:16:17'),
(3311, 2, 1, '2025-07-22 16:16:17'),
(3312, 2, 12, '2025-07-22 16:16:17'),
(3313, 2, 12, '2025-07-22 16:17:05'),
(3314, 2, 13, '2025-07-22 16:17:31'),
(3315, 2, 13, '2025-07-22 16:27:56'),
(3316, 2, 12, '2025-07-22 16:27:56'),
(3317, 2, 1, '2025-07-22 16:27:57'),
(3318, 2, 11, '2025-07-22 16:27:57'),
(3319, 2, 9, '2025-07-22 16:27:57'),
(3320, 2, 11, '2025-07-22 16:28:56'),
(3321, 2, 9, '2025-07-22 16:28:56'),
(3322, 2, 1, '2025-07-22 16:29:02'),
(3323, 2, 12, '2025-07-22 16:29:03'),
(3324, 2, 13, '2025-07-22 16:29:03'),
(3325, 2, 13, '2025-07-22 16:29:55'),
(3326, 1, 13, '2025-07-22 16:32:51'),
(3327, 1, 13, '2025-07-22 16:34:42'),
(3328, 1, 13, '2025-07-22 16:36:40'),
(3329, 2, 9, '2025-07-22 16:36:58'),
(3330, 1, 12, '2025-07-22 16:37:13'),
(3331, 1, 11, '2025-07-22 16:37:14'),
(3332, 1, 11, '2025-07-22 16:46:56'),
(3333, 1, 9, '2025-07-22 16:46:56'),
(3334, 1, 11, '2025-07-22 17:07:00'),
(3335, 1, 9, '2025-07-22 17:07:00'),
(3336, 1, 1, '2025-07-22 17:07:01'),
(3337, 1, 9, '2025-07-22 17:14:32'),
(3338, 1, 11, '2025-07-22 17:14:32'),
(3339, 1, 1, '2025-07-22 17:14:33'),
(3340, 1, 1, '2025-07-22 17:16:37'),
(3341, 1, 9, '2025-07-22 17:16:37'),
(3342, 1, 9, '2025-07-22 17:19:56'),
(3343, 1, 11, '2025-07-22 17:19:56');

-- --------------------------------------------------------

--
-- Estrutura para tabela `visualizacoes_perfis`
--

CREATE TABLE `visualizacoes_perfis` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `perfil_id` int(11) NOT NULL,
  `data_visualizacao` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `visualizacoes_perfis`
--

INSERT INTO `visualizacoes_perfis` (`id`, `usuario_id`, `perfil_id`, `data_visualizacao`) VALUES
(1, 1, 2, '2025-07-22 15:46:46'),
(2, 1, 2, '2025-07-22 15:46:51'),
(3, 2, 1, '2025-07-22 15:47:35'),
(4, 2, 1, '2025-07-22 15:47:37'),
(5, 2, 1, '2025-07-22 15:48:33'),
(6, 2, 1, '2025-07-22 16:05:49'),
(7, 2, 1, '2025-07-22 16:05:51'),
(8, 1, 2, '2025-07-22 16:06:07'),
(9, 2, 1, '2025-07-22 16:09:00'),
(10, 2, 1, '2025-07-22 16:09:03'),
(11, 2, 1, '2025-07-22 16:10:46'),
(12, 1, 2, '2025-07-22 16:32:48'),
(13, 1, 2, '2025-07-22 16:34:16'),
(14, 1, 2, '2025-07-22 16:34:31'),
(15, 1, 2, '2025-07-22 16:35:24'),
(16, 1, 2, '2025-07-22 16:35:37'),
(17, 1, 2, '2025-07-22 16:36:31'),
(18, 2, 1, '2025-07-22 16:36:57');

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `adm`
--
ALTER TABLE `adm`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `bloqueados`
--
ALTER TABLE `bloqueados`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario_id` (`usuario_id`,`bloqueado_id`),
  ADD KEY `bloqueado_id` (`bloqueado_id`);

--
-- Índices de tabela `comentarios`
--
ALTER TABLE `comentarios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `fk_parent_comment` (`parent_comment_id`);

--
-- Índices de tabela `comentario_mencoes`
--
ALTER TABLE `comentario_mencoes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `comentario_id` (`comentario_id`),
  ADD KEY `user_mencionado_id` (`user_mencionado_id`);

--
-- Índices de tabela `curtidas`
--
ALTER TABLE `curtidas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `post_id` (`post_id`,`usuario_id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Índices de tabela `denuncias`
--
ALTER TABLE `denuncias`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_denunciante` (`id_denunciante`),
  ADD KEY `tipo` (`tipo`,`id_alvo`);

--
-- Índices de tabela `hashtags`
--
ALTER TABLE `hashtags`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nome` (`nome`);

--
-- Índices de tabela `historico_pesquisa_post`
--
ALTER TABLE `historico_pesquisa_post`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `un_usuario_termo` (`usuario_id`,`termo`);

--
-- Índices de tabela `historico_pesquisa_procurar_usuarios`
--
ALTER TABLE `historico_pesquisa_procurar_usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_usuario_pesquisado` (`usuario_id`,`usuario_pesquisado_id`),
  ADD KEY `usuario_pesquisado_id` (`usuario_pesquisado_id`),
  ADD KEY `idx_usuario` (`usuario_id`);

--
-- Índices de tabela `mensagens`
--
ALTER TABLE `mensagens`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_remetente` (`id_remetente`),
  ADD KEY `fk_destinatario` (`id_destinatario`);

--
-- Índices de tabela `notificacoes`
--
ALTER TABLE `notificacoes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `origem_usuario_id` (`origem_usuario_id`),
  ADD KEY `post_id` (`post_id`);

--
-- Índices de tabela `pedidos_seguir`
--
ALTER TABLE `pedidos_seguir`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id_solicitante` (`id_solicitante`,`id_destino`),
  ADD KEY `id_destino` (`id_destino`);

--
-- Índices de tabela `pesquisas`
--
ALTER TABLE `pesquisas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Índices de tabela `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `users_id` (`users_id`);

--
-- Índices de tabela `posts_republicados`
--
ALTER TABLE `posts_republicados`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unico_republicado` (`usuario_id`,`post_id`),
  ADD KEY `fk_repub_post` (`post_id`);

--
-- Índices de tabela `posts_salvos`
--
ALTER TABLE `posts_salvos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unico_salvo` (`usuario_id`,`post_id`),
  ADD KEY `fk_posts_salvos_post` (`post_id`);

--
-- Índices de tabela `post_hashtags`
--
ALTER TABLE `post_hashtags`
  ADD PRIMARY KEY (`post_id`,`hashtag_id`),
  ADD KEY `hashtag_id` (`hashtag_id`);

--
-- Índices de tabela `post_mencoes`
--
ALTER TABLE `post_mencoes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `user_mencionado_id` (`user_mencionado_id`);

--
-- Índices de tabela `recuperacao_senha`
--
ALTER TABLE `recuperacao_senha`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Índices de tabela `seguindo`
--
ALTER TABLE `seguindo`
  ADD PRIMARY KEY (`id_seguidor`,`id_seguindo`),
  ADD KEY `id_seguindo` (`id_seguindo`);

--
-- Índices de tabela `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `codigo_user` (`codigo_user`);

--
-- Índices de tabela `visualizacoes`
--
ALTER TABLE `visualizacoes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `post_id` (`post_id`);

--
-- Índices de tabela `visualizacoes_perfis`
--
ALTER TABLE `visualizacoes_perfis`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `perfil_id` (`perfil_id`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `adm`
--
ALTER TABLE `adm`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT de tabela `bloqueados`
--
ALTER TABLE `bloqueados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de tabela `comentarios`
--
ALTER TABLE `comentarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT de tabela `comentario_mencoes`
--
ALTER TABLE `comentario_mencoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de tabela `curtidas`
--
ALTER TABLE `curtidas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT de tabela `denuncias`
--
ALTER TABLE `denuncias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de tabela `hashtags`
--
ALTER TABLE `hashtags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de tabela `historico_pesquisa_post`
--
ALTER TABLE `historico_pesquisa_post`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de tabela `historico_pesquisa_procurar_usuarios`
--
ALTER TABLE `historico_pesquisa_procurar_usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT de tabela `mensagens`
--
ALTER TABLE `mensagens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- AUTO_INCREMENT de tabela `notificacoes`
--
ALTER TABLE `notificacoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de tabela `pedidos_seguir`
--
ALTER TABLE `pedidos_seguir`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- AUTO_INCREMENT de tabela `pesquisas`
--
ALTER TABLE `pesquisas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de tabela `posts`
--
ALTER TABLE `posts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT de tabela `posts_republicados`
--
ALTER TABLE `posts_republicados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=167;

--
-- AUTO_INCREMENT de tabela `posts_salvos`
--
ALTER TABLE `posts_salvos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT de tabela `post_mencoes`
--
ALTER TABLE `post_mencoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de tabela `recuperacao_senha`
--
ALTER TABLE `recuperacao_senha`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- AUTO_INCREMENT de tabela `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de tabela `visualizacoes`
--
ALTER TABLE `visualizacoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3344;

--
-- AUTO_INCREMENT de tabela `visualizacoes_perfis`
--
ALTER TABLE `visualizacoes_perfis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- Restrições para tabelas despejadas
--

--
-- Restrições para tabelas `bloqueados`
--
ALTER TABLE `bloqueados`
  ADD CONSTRAINT `bloqueados_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `bloqueados_ibfk_2` FOREIGN KEY (`bloqueado_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `comentarios`
--
ALTER TABLE `comentarios`
  ADD CONSTRAINT `comentarios_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `comentarios_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_parent_comment` FOREIGN KEY (`parent_comment_id`) REFERENCES `comentarios` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `comentario_mencoes`
--
ALTER TABLE `comentario_mencoes`
  ADD CONSTRAINT `comentario_mencoes_ibfk_1` FOREIGN KEY (`comentario_id`) REFERENCES `comentarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `comentario_mencoes_ibfk_2` FOREIGN KEY (`user_mencionado_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `curtidas`
--
ALTER TABLE `curtidas`
  ADD CONSTRAINT `curtidas_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `curtidas_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `denuncias`
--
ALTER TABLE `denuncias`
  ADD CONSTRAINT `denuncias_ibfk_1` FOREIGN KEY (`id_denunciante`) REFERENCES `users` (`id`);

--
-- Restrições para tabelas `historico_pesquisa_post`
--
ALTER TABLE `historico_pesquisa_post`
  ADD CONSTRAINT `historico_pesquisa_post_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `historico_pesquisa_procurar_usuarios`
--
ALTER TABLE `historico_pesquisa_procurar_usuarios`
  ADD CONSTRAINT `historico_pesquisa_procurar_usuarios_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `historico_pesquisa_procurar_usuarios_ibfk_2` FOREIGN KEY (`usuario_pesquisado_id`) REFERENCES `users` (`id`);

--
-- Restrições para tabelas `mensagens`
--
ALTER TABLE `mensagens`
  ADD CONSTRAINT `fk_destinatario` FOREIGN KEY (`id_destinatario`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `fk_remetente` FOREIGN KEY (`id_remetente`) REFERENCES `users` (`id`);

--
-- Restrições para tabelas `notificacoes`
--
ALTER TABLE `notificacoes`
  ADD CONSTRAINT `notificacoes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `notificacoes_ibfk_2` FOREIGN KEY (`origem_usuario_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `notificacoes_ibfk_3` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`);

--
-- Restrições para tabelas `pedidos_seguir`
--
ALTER TABLE `pedidos_seguir`
  ADD CONSTRAINT `pedidos_seguir_ibfk_1` FOREIGN KEY (`id_solicitante`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `pedidos_seguir_ibfk_2` FOREIGN KEY (`id_destino`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `pesquisas`
--
ALTER TABLE `pesquisas`
  ADD CONSTRAINT `pesquisas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`);

--
-- Restrições para tabelas `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `posts_republicados`
--
ALTER TABLE `posts_republicados`
  ADD CONSTRAINT `fk_repub_post` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_repub_user` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `posts_salvos`
--
ALTER TABLE `posts_salvos`
  ADD CONSTRAINT `fk_posts_salvos_post` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_posts_salvos_user` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `post_hashtags`
--
ALTER TABLE `post_hashtags`
  ADD CONSTRAINT `post_hashtags_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `post_hashtags_ibfk_2` FOREIGN KEY (`hashtag_id`) REFERENCES `hashtags` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `post_mencoes`
--
ALTER TABLE `post_mencoes`
  ADD CONSTRAINT `post_mencoes_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`),
  ADD CONSTRAINT `post_mencoes_ibfk_2` FOREIGN KEY (`user_mencionado_id`) REFERENCES `users` (`id`);

--
-- Restrições para tabelas `recuperacao_senha`
--
ALTER TABLE `recuperacao_senha`
  ADD CONSTRAINT `recuperacao_senha_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Restrições para tabelas `seguindo`
--
ALTER TABLE `seguindo`
  ADD CONSTRAINT `seguindo_ibfk_1` FOREIGN KEY (`id_seguidor`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `seguindo_ibfk_2` FOREIGN KEY (`id_seguindo`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `visualizacoes`
--
ALTER TABLE `visualizacoes`
  ADD CONSTRAINT `visualizacoes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `visualizacoes_ibfk_2` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `visualizacoes_perfis`
--
ALTER TABLE `visualizacoes_perfis`
  ADD CONSTRAINT `visualizacoes_perfis_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `visualizacoes_perfis_ibfk_2` FOREIGN KEY (`perfil_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
