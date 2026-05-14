package com.example.demo.service.impl;

import com.example.demo.dto.*;
import com.example.demo.entity.User;
import com.example.demo.exception.BusinessException;
import com.example.demo.exception.ErrorCode;
import com.example.demo.repository.UserRepository;
import com.example.demo.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;

    @Override
    @Transactional
    public UserResponseDTO create(UserCreateDTO dto) {
        if (userRepository.existsByUsername(dto.getUsername())) {
            throw new BusinessException(ErrorCode.USERNAME_ALREADY_EXISTS);
        }
        if (userRepository.existsByEmail(dto.getEmail())) {
            throw new BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS);
        }

        User user = User.builder()
                .username(dto.getUsername())
                .password(dto.getPassword())
                .email(dto.getEmail())
                .phone(dto.getPhone())
                .nickname(dto.getNickname())
                .status(dto.getStatus())
                .build();

        User saved = userRepository.save(user);
        log.info("创建用户成功: {}", saved.getUsername());
        return toResponseDTO(saved);
    }

    @Override
    @Transactional
    public UserResponseDTO update(Long id, UserUpdateDTO dto) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        if (dto.getUsername() != null && !dto.getUsername().equals(user.getUsername())) {
            if (userRepository.existsByUsername(dto.getUsername())) {
                throw new BusinessException(ErrorCode.USERNAME_ALREADY_EXISTS);
            }
            user.setUsername(dto.getUsername());
        }

        if (dto.getEmail() != null && !dto.getEmail().equals(user.getEmail())) {
            if (userRepository.existsByEmail(dto.getEmail())) {
                throw new BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS);
            }
            user.setEmail(dto.getEmail());
        }

        if (dto.getPassword() != null) {
            user.setPassword(dto.getPassword());
        }
        if (dto.getPhone() != null) {
            user.setPhone(dto.getPhone());
        }
        if (dto.getNickname() != null) {
            user.setNickname(dto.getNickname());
        }
        if (dto.getStatus() != null) {
            user.setStatus(dto.getStatus());
        }

        User updated = userRepository.save(user);
        log.info("更新用户成功: {}", updated.getUsername());
        return toResponseDTO(updated);
    }

    @Override
    @Transactional
    public void delete(Long id) {
        if (!userRepository.existsById(id)) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }
        userRepository.deleteById(id);
        log.info("删除用户成功: id={}", id);
    }

    @Override
    public UserResponseDTO getById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        return toResponseDTO(user);
    }

    @Override
    public UserResponseDTO getByUsername(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        return toResponseDTO(user);
    }

    @Override
    public PageResponse<UserResponseDTO> page(PageRequest request) {
        Pageable pageable = createPageable(request);
        Page<User> page = userRepository.findAll(pageable);
        List<UserResponseDTO> dtoList = page.getContent().stream()
                .map(this::toResponseDTO)
                .collect(Collectors.toList());
        return PageResponse.of(page.getTotalElements(), request.getPage(), request.getSize(), dtoList);
    }

    @Override
    public PageResponse<UserResponseDTO> search(String keyword, PageRequest request) {
        Pageable pageable = createPageable(request);
        Page<User> page = userRepository.searchByKeyword(keyword, pageable);
        List<UserResponseDTO> dtoList = page.getContent().stream()
                .map(this::toResponseDTO)
                .collect(Collectors.toList());
        return PageResponse.of(page.getTotalElements(), request.getPage(), request.getSize(), dtoList);
    }

    @Override
    public List<UserResponseDTO> getByStatus(Integer status) {
        return userRepository.findByStatus(status).stream()
                .map(this::toResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    public long countByStatus(Integer status) {
        return userRepository.countByStatus(status);
    }

    @Override
    @Transactional
    public UserResponseDTO changeStatus(Long id, Integer status) {
        int updated = userRepository.updateStatus(id, status);
        if (updated == 0) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }
        log.info("修改用户状态成功: id={}, status={}", id, status);
        return getById(id);
    }

    @Override
    @Transactional
    public void batchDelete(List<Long> ids) {
        for (Long id : ids) {
            if (!userRepository.existsById(id)) {
                throw new BusinessException(ErrorCode.USER_NOT_FOUND, "ID: " + id);
            }
        }
        userRepository.deleteAllById(ids);
        log.info("批量删除用户成功: ids={}", ids);
    }

    private Pageable createPageable(PageRequest request) {
        Sort.Direction direction = "desc".equalsIgnoreCase(request.getSortOrder())
                ? Sort.Direction.DESC : Sort.Direction.ASC;
        Sort sort = Sort.by(direction, request.getSortBy() != null ? request.getSortBy() : "id");
        return PageRequest.of(request.getPage() - 1, request.getSize(), sort);
    }

    private UserResponseDTO toResponseDTO(User user) {
        return UserResponseDTO.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .phone(user.getPhone())
                .nickname(user.getNickname())
                .status(user.getStatus())
                .createTime(user.getCreateTime())
                .updateTime(user.getUpdateTime())
                .build();
    }
}
