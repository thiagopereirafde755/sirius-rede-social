-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3308
-- Tempo de geração: 21/07/2025 às 21:54
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

-- --------------------------------------------------------

--
-- Estrutura para tabela `hashtags`
--

CREATE TABLE `hashtags` (
  `id` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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

-- --------------------------------------------------------

--
-- Estrutura para tabela `post_hashtags`
--

CREATE TABLE `post_hashtags` (
  `post_id` int(11) NOT NULL,
  `hashtag_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `comentario_mencoes`
--
ALTER TABLE `comentario_mencoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `curtidas`
--
ALTER TABLE `curtidas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `denuncias`
--
ALTER TABLE `denuncias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `hashtags`
--
ALTER TABLE `hashtags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `historico_pesquisa_post`
--
ALTER TABLE `historico_pesquisa_post`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `historico_pesquisa_procurar_usuarios`
--
ALTER TABLE `historico_pesquisa_procurar_usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `mensagens`
--
ALTER TABLE `mensagens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `notificacoes`
--
ALTER TABLE `notificacoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `pedidos_seguir`
--
ALTER TABLE `pedidos_seguir`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- AUTO_INCREMENT de tabela `pesquisas`
--
ALTER TABLE `pesquisas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `posts`
--
ALTER TABLE `posts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `posts_republicados`
--
ALTER TABLE `posts_republicados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `posts_salvos`
--
ALTER TABLE `posts_salvos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `post_mencoes`
--
ALTER TABLE `post_mencoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `recuperacao_senha`
--
ALTER TABLE `recuperacao_senha`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `visualizacoes`
--
ALTER TABLE `visualizacoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `visualizacoes_perfis`
--
ALTER TABLE `visualizacoes_perfis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

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
