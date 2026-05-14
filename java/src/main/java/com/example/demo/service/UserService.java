package com.example.demo.service;

import com.example.demo.dto.*;
import com.example.demo.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface UserService {

    UserResponseDTO create(UserCreateDTO dto);

    UserResponseDTO update(Long id, UserUpdateDTO dto);

    void delete(Long id);

    UserResponseDTO getById(Long id);

    UserResponseDTO getByUsername(String username);

    PageResponse<UserResponseDTO> page(PageRequest request);

    PageResponse<UserResponseDTO> search(String keyword, PageRequest request);

    List<UserResponseDTO> getByStatus(Integer status);

    long countByStatus(Integer status);

    UserResponseDTO changeStatus(Long id, Integer status);

    void batchDelete(List<Long> ids);
}
